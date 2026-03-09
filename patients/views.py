from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .models import PatientProfile, PredictionHistory
from appointments.models import Appointment, Prescription
from accounts.models import UserProfile


@login_required(login_url='patient_login')
def dashboard(request):
    """Patient dashboard"""
    # Check if user is a patient
    try:
        profile = request.user.user_profile
        if profile.role != 'patient':
            return redirect('doctor_dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('patient_login')
    
    # Get patient's data
    try:
        patient_profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        patient_profile = PatientProfile.objects.create(user=request.user)
    
    recent_predictions = PredictionHistory.objects.filter(patient=request.user)[:10]
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date')[:5]
    prescriptions = Prescription.objects.filter(patient=request.user).order_by('-created_at')[:5]
    
    context = {
        'patient_profile': patient_profile,
        'recent_predictions': recent_predictions,
        'appointments': appointments,
        'prescriptions': prescriptions,
    }
    
    return render(request, 'patients/dashboard.html', context)


@login_required(login_url='patient_login')
def profile_view(request):
    """Patient profile view"""
    try:
        profile = request.user.user_profile
        if profile.role != 'patient':
            return redirect('doctor_dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('patient_login')
    
    try:
        patient_profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        patient_profile = PatientProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update patient profile
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        patient_profile.blood_type = request.POST.get('blood_type', '')
        patient_profile.allergies = request.POST.get('allergies', '')
        patient_profile.medical_history = request.POST.get('medical_history', '')
        patient_profile.emergency_contact = request.POST.get('emergency_contact', '')
        patient_profile.emergency_phone = request.POST.get('emergency_phone', '')
        patient_profile.save()
        
        profile.phone = request.POST.get('phone', '')
        profile.bio = request.POST.get('bio', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('patient_profile')
    
    context = {
        'patient_profile': patient_profile,
    }
    
    return render(request, 'patients/profile.html', context)


@login_required(login_url='patient_login')
def prediction_history(request):
    """View prediction history"""
    try:
        profile = request.user.user_profile
        if profile.role != 'patient':
            return redirect('doctor_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('patient_login')
    
    predictions = PredictionHistory.objects.filter(patient=request.user).order_by('-created_at')
    
    context = {
        'predictions': predictions,
    }
    
    return render(request, 'patients/prediction_history.html', context)


@login_required(login_url='patient_login')
def view_doctors(request):
    """View list of available doctors"""
    try:
        profile = request.user.user_profile
        if profile.role != 'patient':
            return redirect('doctor_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('patient_login')
    
    from doctors.models import DoctorProfile
    doctors = DoctorProfile.objects.filter(is_verified=True).select_related('user')
    
    context = {
        'doctors': doctors,
    }
    
    return render(request, 'patients/view_doctors.html', context)
