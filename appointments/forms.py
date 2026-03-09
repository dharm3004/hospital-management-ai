from django import forms
from .models import Appointment, Prescription


class AppointmentBookingForm(forms.ModelForm):
    """Form for booking appointments"""
    class Meta:
        model = Appointment
        fields = ('doctor', 'date', 'reason')
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': 'required'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your symptoms or reason for appointment'
            }),
        }


class PrescriptionForm(forms.ModelForm):
    """Form for creating prescriptions"""
    class Meta:
        model = Prescription
        fields = ('medication', 'frequency', 'duration', 'instructions', 'notes')
        widgets = {
            'medication': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medication name and dosage'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Once daily, Twice daily'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 7 days, 2 weeks'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special instructions'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }
