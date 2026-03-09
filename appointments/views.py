from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Appointment, Prescription
from .forms import AppointmentBookingForm, PrescriptionForm
from accounts.models import UserProfile
from doctors.models import DoctorProfile, DoctorAvailability
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
import datetime


@login_required(login_url='patient_login')
def book_appointment(request):
    """Book an appointment"""
    try:
        profile = request.user.user_profile
        if profile.role != 'patient':
            return redirect('doctor_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('patient_login')
    
    # Provide departments and doctors for the multi-step booking UI
    doctors_qs = User.objects.filter(doctor_profile__isnull=False).select_related('doctor_profile')
    departments = [c[0] for c in DoctorProfile.SPECIALIZATION_CHOICES]

    if request.method == 'POST':
        # Expect fields: doctor (id), date (YYYY-MM-DD), time (HH:MM), reason
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        reason = request.POST.get('reason', '')

        if not (doctor_id and date_str and time_str):
            messages.error(request, 'Please select doctor, date and time')
            return redirect('book_appointment')

        try:
            doctor = User.objects.get(id=int(doctor_id))
        except Exception:
            messages.error(request, 'Selected doctor not found')
            return redirect('book_appointment')

        try:
            dt_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            dt_time = datetime.datetime.strptime(time_str, '%H:%M').time()
            dt = datetime.datetime.combine(dt_date, dt_time)
        except Exception:
            messages.error(request, 'Invalid date or time')
            return redirect('book_appointment')

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            date=dt,
            reason=reason,
            status='pending'
        )
        messages.success(request, 'Appointment confirmed')
        return redirect('patient_dashboard')

    context = {
        'doctors': doctors_qs,
        'departments': departments,
    }
    return render(request, 'appointments/book.html', context)


def available_slots(request):
    """Return available time slots for a doctor on a given date.

    Query params: doctor_id, date (YYYY-MM-DD)
    """
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    if not (doctor_id and date_str):
        return HttpResponseBadRequest('doctor_id and date are required')
    try:
        doctor = User.objects.get(id=int(doctor_id))
    except Exception:
        return HttpResponseBadRequest('Invalid doctor')
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return HttpResponseBadRequest('Invalid date')

    slots = DoctorAvailability.objects.filter(doctor=doctor, date=date, is_available=True).order_by('start_time')
    data = [{'start': s.start_time.strftime('%H:%M'), 'end': s.end_time.strftime('%H:%M')} for s in slots]
    return JsonResponse({'slots': data})


@login_required(login_url='doctor_login')
def create_prescription(request, appointment_id):
    """Create prescription for an appointment"""
    try:
        profile = request.user.user_profile
        if profile.role != 'doctor':
            return redirect('patient_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('doctor_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.doctor = request.user
            prescription.patient = appointment.patient
            prescription.save()
            messages.success(request, 'Prescription created successfully!')
            return redirect('doctor_manage_appointments')
    else:
        form = PrescriptionForm()
    
    context = {
        'appointment': appointment,
        'form': form,
    }
    
    return render(request, 'appointments/create_prescription.html', context)


@login_required(login_url='patient_login')
def view_prescriptions(request):
    """View patient prescriptions"""
    try:
        profile = request.user.user_profile
        if profile.role != 'patient':
            return redirect('doctor_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('patient_login')
    
    prescriptions = Prescription.objects.filter(patient=request.user).order_by('-created_at')
    
    context = {
        'prescriptions': prescriptions,
    }
    
    return render(request, 'appointments/view_prescriptions.html', context)
