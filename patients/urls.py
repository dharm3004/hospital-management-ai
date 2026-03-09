from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='patient_dashboard'),
    path('profile/', views.profile_view, name='patient_profile'),
    path('prediction-history/', views.prediction_history, name='patient_prediction_history'),
    path('doctors/', views.view_doctors, name='view_doctors'),
]
