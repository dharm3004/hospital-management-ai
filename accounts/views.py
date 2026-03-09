from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import Group, User
from .forms import PatientRegistrationForm, DoctorRegistrationForm, PatientLoginForm, DoctorLoginForm
from .models import UserProfile


@require_http_methods(["GET", "POST"])
def patient_register(request):
    """Patient registration view"""
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Assign Patient group
            patient_group, created = Group.objects.get_or_create(name='Patient')
            user.groups.add(patient_group)

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('patient_login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'accounts/patient_register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def doctor_register(request):
    """Doctor registration view"""
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile for doctor
            UserProfile.objects.create(user=user, role='doctor', phone=form.cleaned_data.get('phone', ''))

            # Create doctor profile
            from doctors.models import DoctorProfile
            DoctorProfile.objects.create(
                user=user,
                license_number=form.cleaned_data.get('license_number'),
                specialization=form.cleaned_data.get('specialization')
            )

            # Assign Doctor group
            doctor_group, created = Group.objects.get_or_create(name='Doctor')
            user.groups.add(doctor_group)

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('doctor_login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'accounts/doctor_register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def patient_login(request):
    """Patient login view"""
    if request.method == 'POST':
        form = PatientLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Verify user is patient
            try:
                profile = user.user_profile
                if profile.role != 'patient':
                    messages.error(request, 'This account is not registered as a patient.')
                    return redirect('patient_login')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found.')
                return redirect('patient_login')
            
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}!')
            return redirect('patient_dashboard')
        else:
            # Show generic authentication error
            messages.error(request, 'Invalid username or password')
    else:
        form = PatientLoginForm()
    
    return render(request, 'accounts/patient_login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def doctor_login(request):
    """Doctor login view"""
    if request.method == 'POST':
        form = DoctorLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Verify user is doctor
            try:
                profile = user.user_profile
                if profile.role != 'doctor':
                    messages.error(request, 'This account is not registered as a doctor.')
                    return redirect('doctor_login')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found.')
                return redirect('doctor_login')
            
            login(request, user)
            messages.success(request, f'Welcome, Dr. {user.first_name or user.username}!')
            return redirect('doctor_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = DoctorLoginForm()
    
    return render(request, 'accounts/doctor_login.html', {'form': form})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
