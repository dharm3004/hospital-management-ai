from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone


class PatientProfile(models.Model):
    """Extended patient profile with medical information"""
    BLOOD_TYPE_CHOICES = (
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True, help_text='List any known allergies')
    medical_history = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'

    def __str__(self):
        return f"Patient: {self.user.username}"


class PredictionHistory(models.Model):
    """AI diagnosis history for patients"""
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prediction_history')
    symptoms = models.JSONField(encoder=DjangoJSONEncoder, help_text='Selected symptoms')
    results = models.JSONField(encoder=DjangoJSONEncoder, help_text='Diagnosis results')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Prediction History'
        verbose_name_plural = 'Prediction Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"Prediction {self.id} - {self.patient.username} ({self.created_at})"
