# authentication/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patient-area/', views.patient_only_view, name='patient_only'),
    path('doctor-area/', views.doctor_only_view, name='doctor_only'),
]