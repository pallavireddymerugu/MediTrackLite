from django.db import models
# authentication/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_patient(self):
        return self.role == 'patient'
    
    def is_doctor(self):
        return self.role == 'doctor'