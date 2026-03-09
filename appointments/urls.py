from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('<int:appointment_id>/prescription/', views.create_prescription, name='create_prescription'),
    path('prescriptions/', views.view_prescriptions, name='view_prescriptions'),
    path('available-slots/', views.available_slots, name='available_slots'),
]
