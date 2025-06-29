from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

User = get_user_model()

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments', null=True, blank=True)
    preferred_doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferred_appointments', null=True, blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    health_concern = models.TextField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def clean(self):
        # Validate appointment time (9 AM to 5 PM)
        if self.appointment_time:
            start_time = datetime.time(9, 0)
            end_time = datetime.time(17, 0)
            if not (start_time <= self.appointment_time <= end_time):
                raise ValidationError('Appointment time must be between 9:00 AM and 5:00 PM')
    
    def can_transition_to(self, new_status):
        transitions = {
            'pending': ['confirmed'],
            'confirmed': ['in_progress'],
            'in_progress': ['completed'],
            'completed': []
        }
        return new_status in transitions.get(self.status, [])
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.appointment_date} {self.appointment_time}"

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    medicine_names = models.TextField()
    dosage_instructions = models.TextField()
    frequency = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prescription for {self.appointment.patient.get_full_name()}"

class Feedback(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.patient.get_full_name()} - Rating: {self.rating}"