from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DoctorProfile(models.Model):
    """Extended doctor profile with professional information"""
    SPECIALIZATION_CHOICES = (
        ('General', 'General Practitioner'),
        ('Cardiology', 'Cardiology'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Dermatology', 'Dermatology'),
        ('Orthopedics', 'Orthopedics'),
        ('Psychiatry', 'Psychiatry'),
        ('Others', 'Others'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES, default='General')
    license_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    experience_years = models.IntegerField(default=0, help_text='Years of experience')
    qualification = models.TextField(blank=True, null=True, help_text='Educational qualifications')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.get_specialization_display()}"


class DoctorAvailability(models.Model):
    """Doctor's availability slots for appointments"""
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Doctor Availability'
        verbose_name_plural = 'Doctor Availabilities'
        unique_together = ('doctor', 'date', 'start_time', 'end_time')
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.doctor} - {self.date} ({self.start_time}-{self.end_time})"
