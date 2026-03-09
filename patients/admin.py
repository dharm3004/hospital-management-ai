from django.contrib import admin
from .models import PatientProfile, PredictionHistory


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_type', 'created_at')
    list_filter = ('blood_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('patient__username',)
    readonly_fields = ('created_at',)
