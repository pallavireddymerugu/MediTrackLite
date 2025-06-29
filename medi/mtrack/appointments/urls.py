from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('list/', views.appointments_list, name='appointments_list'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('accept/<int:appointment_id>/', views.accept_appointment, name='accept_appointment'),
    path('detail/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('update-status/<int:appointment_id>/', views.update_appointment_status, name='update_status'),
    path('add-prescription/<int:appointment_id>/', views.add_prescription, name='add_prescription'),
    path('submit-feedback/<int:appointment_id>/', views.submit_feedback, name='submit_feedback'),
]