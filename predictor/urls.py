from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # AI diagnosis route (reintroduced)
    path('ai-diagnosis/', views.ai_diagnosis, name='ai_diagnosis'),
    path('doctors/', views.doctors_page, name='doctors_list'),
    path('departments/', views.departments_page, name='departments'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('emergency/', views.emergency_page, name='emergency'),
    path('news/', views.news_page, name='news'),
    path('chat/', views.chat_page, name='chat'),
    path('chat/send/', views.send_message, name='chat_send'),
    path('chat/fetch/<int:user_id>/', views.fetch_messages, name='chat_fetch'),
    # AI chat assistant (public)
    path('chat/assistant/', views.ai_chat, name='chat_assistant'),
    path('chat/assistant/api/', views.ai_chat_api, name='chat_assistant_api'),
    path('diseases/', views.disease_list, name='disease_list'),
    path('disease/info/<str:name>/json/', views.disease_info_json, name='disease_info_json'),
    path('disease/<int:pk>/', views.disease_detail, name='disease_detail'),
    path('disease/<str:name>/', views.disease_detail, name='disease_detail_by_name'),
]
