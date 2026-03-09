from django.urls import path
from . import views

urlpatterns = [
    path('patient/register/', views.patient_register, name='patient_register'),
    path('doctor/register/', views.doctor_register, name='doctor_register'),
    path('patient/login/', views.patient_login, name='patient_login'),
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('logout/', views.logout_view, name='logout'),
]
