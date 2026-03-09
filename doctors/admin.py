from django.contrib import admin
from .models import DoctorProfile, DoctorAvailability


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'is_verified', 'created_at')
    list_filter = ('specialization', 'is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'license_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'is_available')
    search_fields = ('doctor__username',)
    readonly_fields = ('created_at',)
