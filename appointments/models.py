from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Appointment(models.Model):
    """Appointment between patient and doctor"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no-show', 'No Show'),
    )
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True, help_text='Doctor notes during appointment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['doctor', 'status']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"Appointment #{self.id} - {self.patient.username} with Dr. {self.doctor.username}"


class Prescription(models.Model):
    """Prescription issued by doctor to patient"""
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions_issued')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions_received')
    
    medication = models.CharField(max_length=255, help_text='Medication name and dosage')
    frequency = models.CharField(max_length=100, help_text='e.g., Once daily, Twice daily')
    duration = models.CharField(max_length=100, help_text='e.g., 7 days, 2 weeks')
    instructions = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription #{self.id} - {self.patient.username} by Dr. {self.doctor.username}"


class Message(models.Model):
    """Simple chat message between users (patient and doctor)"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
