from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home and prediction
    path('', include('predictor.urls')),
    
    # Authentication
    path('auth/', include('accounts.urls')),
    
    # Patient URLs
    path('patient/', include('patients.urls')),
    
    # Doctor URLs
    path('doctor/', include('doctors.urls')),
    
    # Appointments
    path('appointment/', include('appointments.urls')),
]
