# authentication/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User
import re

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check for duplicate email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        
        # Validate @meditrack.local domain
        if not email.endswith('@meditrack.local'):
            raise forms.ValidationError("Email must end with @meditrack.local")
        
        return email
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        
        # Password must be hashed - this is handled by Django automatically
        # But we can add custom validation here
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return password
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))