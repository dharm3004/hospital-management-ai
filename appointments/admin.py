from django.contrib import admin
from .models import Appointment, Prescription


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'status')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('patient__username', 'doctor__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'medication', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('patient__username', 'doctor__username', 'medication')
    readonly_fields = ('created_at', 'updated_at')
