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
    # basic input validation
    if not isinstance(symptoms, list):
        return JsonResponse({'error': 'Invalid symptoms format.'}, status=400)
    symptoms = [str(s).strip() for s in symptoms if str(s).strip()]
    if not symptoms:
        return JsonResponse({'error': 'Please select at least one symptom'}, status=400)
    if len(symptoms) > 30:
        return JsonResponse({'error': 'Too many symptoms selected. Please choose the most important ones.'}, status=400)

    # whether to save this prediction to history (default: True for backwards compatibility)
    save_history_flag = data.get('save_history')
    if save_history_flag is None:
        save_history = True
    else:
        save_history = bool(save_history_flag)

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

    # if the user is a logged-in patient and opted in, record this prediction
    if request.user.is_authenticated and save_history and results:
        try:
            if hasattr(request.user, 'user_profile') and request.user.user_profile.role == 'patient':
                PredictionHistory.objects.create(patient=request.user, symptoms=symptoms, results=results)
        except Exception:
            # don't let history failures affect API
            pass

    summary = None
    if results:
        top = results[0]
        summary = f"Most likely condition: {top['disease']} ({top['probability']}% confidence) based on {len(symptoms)} symptom(s)."

    return JsonResponse({'results': results, 'summary': summary, 'symptom_count': len(symptoms)})

