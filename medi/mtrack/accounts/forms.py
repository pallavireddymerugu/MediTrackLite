from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    specialization = forms.CharField(max_length=100, required=False)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@meditrack.local'):
            raise ValidationError('Email must end with @meditrack.local')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        specialization = cleaned_data.get('specialization')

        if role == 'doctor' and not specialization:
            self.add_error('specialization', 'Specialization is required for doctors.')

        return cleaned_data
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        user.specialization = self.cleaned_data.get('specialization', '')
        if commit:
            user.save()
        return user
