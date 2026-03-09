from django.contrib import admin
from .models import DiseaseInfo


@admin.register(DiseaseInfo)
class DiseaseInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('name', 'symptoms')
    readonly_fields = ('created_at', 'updated_at')