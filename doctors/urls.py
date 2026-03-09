from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('profile/', views.profile_view, name='doctor_profile'),
    path('appointments/', views.manage_appointments, name='doctor_manage_appointments'),
    path('appointments/<int:appointment_id>/approve/', views.approve_appointment, name='doctor_approve_appointment'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='doctor_cancel_appointment'),
    path('availability/', views.manage_availability, name='doctor_manage_availability'),
    path('availability/<int:availability_id>/delete/', views.delete_availability, name='doctor_delete_availability'),
]
