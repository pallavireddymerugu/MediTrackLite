from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    def clean(self):
        super().clean()
        if not self.email.endswith('@meditrack.local'):
            from django.core.exceptions import ValidationError
            raise ValidationError('Email must end with @meditrack.local')
    
    def is_patient(self):
        return self.role == 'patient'
    
    def is_doctor(self):
        return self.role == 'doctor'