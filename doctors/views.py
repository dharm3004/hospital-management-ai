from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import DoctorProfile, DoctorAvailability
from appointments.models import Appointment, Prescription
from accounts.models import UserProfile
from patients.models import PredictionHistory


@login_required(login_url='doctor_login')
def dashboard(request):
    """Doctor dashboard"""
    # Check if user is a doctor
    try:
        profile = request.user.user_profile
        if profile.role != 'doctor':
            return redirect('patient_dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('doctor_login')
    
    try:
        doctor_profile = request.user.doctor_profile
    except DoctorProfile.DoesNotExist:
        doctor_profile = DoctorProfile.objects.create(user=request.user)
    
    # Get today's appointments
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    today_appointments = Appointment.objects.filter(
        doctor=request.user,
        date__date=today
    ).order_by('date')
    
    pending_appointments = Appointment.objects.filter(
        doctor=request.user,
        status='pending'
    ).order_by('date')[:5]
    
    recent_predictions = PredictionHistory.objects.all().order_by('-created_at')[:10]
    
    context = {
        'doctor_profile': doctor_profile,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'recent_predictions': recent_predictions,
    }
    
    return render(request, 'doctors/dashboard.html', context)


@login_required(login_url='doctor_login')
def profile_view(request):
    """Doctor profile view"""
    try:
        profile = request.user.user_profile
        if profile.role != 'doctor':
            return redirect('patient_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('doctor_login')
    
    try:
        doctor_profile = request.user.doctor_profile
    except DoctorProfile.DoesNotExist:
        doctor_profile = DoctorProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update doctor profile
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        doctor_profile.specialization = request.POST.get('specialization', '')
        doctor_profile.license_number = request.POST.get('license_number', '')
        doctor_profile.experience_years = int(request.POST.get('experience_years', '0'))
        doctor_profile.qualification = request.POST.get('qualification', '')
        doctor_profile.consultation_fee = request.POST.get('consultation_fee', '0')
        doctor_profile.bio = request.POST.get('bio', '')
        doctor_profile.save()
        
        profile.phone = request.POST.get('phone', '')
        profile.bio = request.POST.get('bio', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('doctor_profile')
    
    context = {
        'doctor_profile': doctor_profile,
    }
    
    return render(request, 'doctors/profile.html', context)


@login_required(login_url='doctor_login')
def manage_appointments(request):
    """Manage patient appointments"""
    try:
        profile = request.user.user_profile
        if profile.role != 'doctor':
            return redirect('patient_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('doctor_login')
    
    appointments = Appointment.objects.filter(doctor=request.user).order_by('-date')
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'appointments': page_obj,
    }
    
    return render(request, 'doctors/manage_appointments.html', context)


@login_required(login_url='doctor_login')
@require_POST
def approve_appointment(request, appointment_id):
    """Approve appointment"""
    try:
        appointment = Appointment.objects.get(id=appointment_id, doctor=request.user)
        appointment.status = 'approved'
        appointment.save()
        messages.success(request, 'Appointment approved!')
        return redirect('doctor_manage_appointments')
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
        return redirect('doctor_manage_appointments')


@login_required(login_url='doctor_login')
@require_POST
def cancel_appointment(request, appointment_id):
    """Cancel appointment"""
    try:
        appointment = Appointment.objects.get(id=appointment_id, doctor=request.user)
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled!')
        return redirect('doctor_manage_appointments')
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
        return redirect('doctor_manage_appointments')


@login_required(login_url='doctor_login')
def manage_availability(request):
    """Manage doctor's availability"""
    try:
        profile = request.user.user_profile
        if profile.role != 'doctor':
            return redirect('patient_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('doctor_login')
    
    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        DoctorAvailability.objects.create(
            doctor=request.user,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        messages.success(request, 'Availability slot added!')
        return redirect('doctor_manage_availability')
    
    availabilities = DoctorAvailability.objects.filter(doctor=request.user).order_by('-date')
    
    context = {
        'availabilities': availabilities,
    }
    
    return render(request, 'doctors/manage_availability.html', context)


@login_required(login_url='doctor_login')
@require_POST
def delete_availability(request, availability_id):
    """Delete availability slot"""
    try:
        availability = DoctorAvailability.objects.get(id=availability_id, doctor=request.user)
        availability.delete()
        messages.success(request, 'Availability slot deleted!')
    except DoctorAvailability.DoesNotExist:
        messages.error(request, 'Availability slot not found.')
    
    return redirect('doctor_manage_availability')
