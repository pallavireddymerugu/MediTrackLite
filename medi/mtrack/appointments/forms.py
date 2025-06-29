from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Appointment, Prescription, Feedback
import datetime

User = get_user_model()

class AppointmentForm(forms.ModelForm):
    preferred_doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='doctor'),
        empty_label="Select a doctor",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    
    health_concern = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )
    
    class Meta:
        model = Appointment
        fields = ['preferred_doctor', 'appointment_date', 'appointment_time', 'health_concern']
    
    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date and date < datetime.date.today():
            raise ValidationError('Appointment date cannot be in the past.')
        return date
    
    def clean_appointment_time(self):
        time = self.cleaned_data.get('appointment_time')
        if time:
            start_time = datetime.time(9, 0)
            end_time = datetime.time(17, 0)
            if not (start_time <= time <= end_time):
                raise ValidationError('Appointment time must be between 9:00 AM and 5:00 PM')
        return time

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicine_names', 'dosage_instructions', 'frequency']
        widgets = {
            'medicine_names': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'dosage_instructions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)], 
                                 attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Optional comment (max 150 characters)'}),
        }