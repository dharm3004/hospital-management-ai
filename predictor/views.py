import os
import json
import pickle

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import DiseaseInfo
from patients.models import PredictionHistory

from accounts.models import UserProfile
from appointments.models import Message
from django.core.mail import send_mail
from django.contrib import messages as django_messages
from django.contrib.auth.models import User
from django.db import models


def home(request):
    """Home/Landing page"""
    disease_count = DiseaseInfo.objects.count()
    context = {
        'disease_count': disease_count,
    }
    # Render the single index template for the homepage to avoid duplicate includes
    return render(request, 'predictor/index.html', context)


def load_model():
    """Load the ML model from pickle file located in BASE_DIR"""
    model_path = os.path.join(settings.BASE_DIR, 'model_data.pkl')
    if not os.path.exists(model_path):
        raise FileNotFoundError('Model file not found')
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    if isinstance(data, dict) and 'model' in data:
        model = data['model']
        features = data.get('features') or data.get('feature_names') or []
    else:
        model = data
        features = []
    return {'model': model, 'features': features}


@require_http_methods(["GET", "POST"])
def ai_diagnosis(request):
    """AI diagnosis view handling GET form display and POST prediction via JSON."""
    # GET: render page with list of symptoms
    if request.method == 'GET':
        try:
            model_data = load_model()
            symptoms = model_data.get('features', [])
        except Exception:
            symptoms = []
        symptoms_json = json.dumps(symptoms)
        return render(request, 'ai_diagnosis.html', {'symptoms': symptoms_json})

    # POST: perform prediction
    try:
        model_data = load_model()
        model = model_data['model']
        features = model_data['features']
    except Exception:
        return JsonResponse({'error': 'AI diagnosis service temporarily unavailable.'}, status=503)

    # parse JSON body
    try:
        raw = request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else ''
        data = json.loads(raw or '{}')
    except Exception:
        data = {'symptoms': request.POST.getlist('symptoms', [])}

    symptoms = data.get('symptoms', []) or []
    if not symptoms:
        return JsonResponse({'error': 'Please select at least one symptom'}, status=400)

    # construct feature vector
    feature_vector = [1 if feat in symptoms else 0 for feat in (features or [])]
    results = []
    try:
        import numpy as np
        X = np.array([feature_vector])
        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba(X)[0]
            labels = getattr(model, 'classes_', None)
            if labels is None:
                labels = [f'Disease {i}' for i in range(len(probs))]
            pairs = list(zip(labels, probs))
            pairs.sort(key=lambda x: x[1], reverse=True)
            for name, prob in pairs[:3]:
                results.append({'disease': str(name), 'probability': round(float(prob) * 100)})
        else:
            preds = model.predict(X)
            if len(preds) > 0:
                results.append({'disease': str(preds[0]), 'probability': 100})
    except Exception:
        return JsonResponse({'error': 'Prediction error.'}, status=500)

    # if the user is a logged-in patient, record this prediction
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'user_profile') and request.user.user_profile.role == 'patient':
                PredictionHistory.objects.create(patient=request.user, symptoms=symptoms, results=results)
        except Exception:
            # don't let history failures affect API
            pass

    return JsonResponse({'results': results})



@require_http_methods(["GET"])
def disease_detail(request, pk=None, name=None):
    """View disease details"""
    if pk:
        disease = get_object_or_404(DiseaseInfo, pk=pk)
    elif name:
        disease = get_object_or_404(DiseaseInfo, name__iexact=name)
    else:
        return redirect('home')
    
    context = {
        'disease': disease,
    }
    
    return render(request, 'predictor/disease_detail.html', context)


@require_http_methods(["GET"])
def disease_list(request):
    """List all diseases"""
    diseases = DiseaseInfo.objects.all().order_by('name')
    search_query = request.GET.get('q', '')
    
    if search_query:
        from django.db.models import Q
        diseases = diseases.filter(
            Q(name__icontains=search_query) |
            Q(symptoms__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    
    context = {
        'diseases': diseases,
        'search_query': search_query,
    }
    
    return render(request, 'predictor/disease_list.html', context)


def doctors_page(request):
    from doctors.models import DoctorProfile
    doctors = DoctorProfile.objects.select_related('user').all()
    return render(request, 'doctors_page.html', {'doctors': doctors})


def departments_page(request):
    depts = [
        {'name': 'Cardiology', 'icon': 'bi-heart-pulse', 'desc': 'Heart and vascular care.'},
        {'name': 'Neurology', 'icon': 'bi-brain', 'desc': 'Brain and nervous system.'},
        {'name': 'Orthopedics', 'icon': 'bi-bandaid', 'desc': 'Bone and joint care.'},
        {'name': 'Pediatrics', 'icon': 'bi-people', 'desc': 'Child health and wellness.'},
        {'name': 'Dermatology', 'icon': 'bi-droplet', 'desc': 'Skin care and treatment.'},
        {'name': 'Radiology', 'icon': 'bi-camera', 'desc': 'Imaging and diagnostics.'},
        {'name': 'Emergency Medicine', 'icon': 'bi-activity', 'desc': 'Emergency and urgent care.'},
    ]
    return render(request, 'departments.html', {'departments': depts})


def about_page(request):
    doctors_count = DiseaseInfo.objects.count()  # reuse as placeholder metric
    return render(request, 'about.html', {'doctors_count': doctors_count})


def contact_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # Send a simple email to site admin if configured
        try:
            send_mail(f'Contact form from {name}', message, email, [settings.DEFAULT_FROM_EMAIL])
            django_messages.success(request, 'Message sent — we will contact you shortly.')
        except Exception:
            django_messages.info(request, 'Message received (email not configured).')
        return redirect('contact')
    return render(request, 'contact.html')


def emergency_page(request):
    info = {
        'hotline': '+1-800-EMERGENCY',
        'ambulance': '+1-800-AMBULANCE',
        'nearest': 'City General Hospital, 123 Health St.',
    }
    return render(request, 'emergency.html', {'info': info})


def news_page(request):
    news = [
        {'title': 'New Cardiology Wing Opens', 'date': '2026-02-10', 'summary': 'State-of-the-art cardiac care.'},
        {'title': 'Free Health Camp', 'date': '2026-03-01', 'summary': 'Community health screenings and vaccinations.'},
    ]
    return render(request, 'news.html', {'news': news})


def ai_chat(request):
    """Public AI chat assistant page.

    This is a lightweight assistant that responds with simple, deterministic
    answers based on keywords. It's intended to be fast and work without
    external API keys. A frontend JS calls `ai_chat_api` to get responses.
    """
    return render(request, 'predictor/chat_assistant.html')


@require_http_methods(['POST'])
def ai_chat_api(request):
    """Simple assistant API that returns a canned response based on input."""
    try:
        data = json.loads(request.body)
    except Exception:
        data = {'message': request.POST.get('message', '')}

    message = (data.get('message') or '').lower()
    # Keyword-driven responses with department recommendation and simple routing
    if not message:
        reply = "Hi — how can I help with your health question today?"
        dept = None
    elif any(k in message for k in ['fever', 'temperature', 'headache', 'flu']):
        reply = "These symptoms may indicate a viral infection or flu. Rest, hydration and paracetamol for fever may help. If symptoms worsen or persist beyond 48 hours, consult a physician."
        dept = 'General'
    elif any(k in message for k in ['cough', 'breath', 'shortness', 'wheezing']):
        reply = "Cough and breathing issues can be caused by infections, asthma or other respiratory conditions. If you have breathing difficulty, seek urgent care. Otherwise book a pulmonary or general medicine appointment."
        dept = 'General'
    elif any(k in message for k in ['skin', 'rash', 'itch', 'dermat']):
        reply = "Skin problems are usually handled by a Dermatologist. Keep the area clean and avoid irritants. See a dermatologist if it spreads or is painful."
        dept = 'Dermatology'
    elif any(k in message for k in ['pain', 'back pain', 'joint', 'fracture']):
        reply = "For musculoskeletal pain consult Orthopedics or Physiotherapy. Avoid heavy lifting and consider OTC analgesics."
        dept = 'Orthopedics'
    elif 'appointment' in message or 'book' in message:
        reply = "You can book an appointment from the Book Appointment page — choose a doctor and preferred slot."
        dept = None
    elif 'which doctor' in message or 'which doctor should' in message or 'who should' in message:
        # attempt to map to department
        if 'skin' in message or 'dermat' in message:
            reply = "You should consult a Dermatologist."
            dept = 'Dermatology'
        elif 'heart' in message or 'cardio' in message:
            reply = "You should consult a Cardiologist."
            dept = 'Cardiology'
        else:
            reply = "If unsure, start with a General Practitioner who can refer you to a specialist."
            dept = 'General'
    else:
        reply = "Thanks for your question. For specific medical advice, please consult a healthcare professional."
        dept = None

    # Try to find a recommended doctor in the dept (if available)
    recommended = None
    if dept:
        try:
            from doctors.models import DoctorProfile
            from django.contrib.auth.models import User
            dp = DoctorProfile.objects.filter(specialization__icontains=dept).select_related('user').first()
            if dp:
                recommended = f"Dr. {dp.user.first_name or dp.user.username} ({dp.get_specialization_display()})"
        except Exception:
            recommended = None

    return JsonResponse({'reply': reply, 'recommended_department': dept, 'recommended_doctor': recommended})


@login_required
def chat_page(request):
    # Show recent conversations for the user
    user = request.user
    # List of unique chat partners
    partners = set()
    msgs = Message.objects.filter(models.Q(sender=user) | models.Q(receiver=user)).select_related('sender', 'receiver')[:200]
    for m in msgs:
        partners.add(m.sender if m.sender != user else m.receiver)
    return render(request, 'chat.html', {'partners': list(partners)})


@require_POST
@login_required
def send_message(request):
    to_id = request.POST.get('to')
    text = request.POST.get('message')
    try:
        to_user = User.objects.get(id=to_id)
    except Exception:
        return JsonResponse({'error': 'Invalid recipient'}, status=400)
    msg = Message.objects.create(sender=request.user, receiver=to_user, message=text)
    return JsonResponse({'ok': True, 'id': msg.id, 'timestamp': msg.timestamp.isoformat()})


@require_http_methods(['GET'])
@login_required
def fetch_messages(request, user_id):
    other = User.objects.get(id=user_id)
    qs = Message.objects.filter(models.Q(sender=request.user, receiver=other) | models.Q(sender=other, receiver=request.user)).order_by('timestamp')
    data = [{'from': m.sender.username, 'to': m.receiver.username, 'message': m.message, 'timestamp': m.timestamp.isoformat()} for m in qs]
    return JsonResponse({'messages': data})


@require_http_methods(["GET"])
def disease_info_json(request, name):
    """Return disease info as JSON for use in UI modals"""
    try:
        disease = DiseaseInfo.objects.get(name__iexact=name)
    except DiseaseInfo.DoesNotExist:
        return JsonResponse({'error': 'Disease not found'}, status=404)

    # Derive simple recommended department by keyword matching in name or symptoms
    rec_dept = None
    keywords = (disease.name + ' ' + (disease.symptoms or '')).lower()
    if any(k in keywords for k in ['cardio', 'heart', 'cardiac']):
        rec_dept = 'Cardiology'
    elif any(k in keywords for k in ['neuro', 'brain', 'seizure', 'stroke']):
        rec_dept = 'Neurology'
    elif any(k in keywords for k in ['skin', 'rash', 'derm']):
        rec_dept = 'Dermatology'
    elif any(k in keywords for k in ['child', 'pediatr']):
        rec_dept = 'Pediatrics'
    else:
        rec_dept = 'General'

    # Try to find a recommended doctor username
    rec_doc = None
    try:
        from doctors.models import DoctorProfile
        dp = DoctorProfile.objects.filter(specialization__icontains=rec_dept).select_related('user').first()
        if dp:
            rec_doc = dp.user.get_full_name() or dp.user.username
    except Exception:
        rec_doc = None

    data = {
        'name': disease.name,
        'short_description': disease.short_description,
        'symptoms': disease.symptoms,
        'prevention': getattr(disease, 'prevention', ''),
        'treatment': getattr(disease, 'treatment', ''),
        'causes': getattr(disease, 'treatment', ''),
        'recommended_department': rec_dept,
        'recommended_doctor': rec_doc,
    }
    return JsonResponse(data)
