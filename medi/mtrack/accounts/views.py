from django.shortcuts import render,redirect

# Create your views here.
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .forms import CustomUserCreationForm
from appointments.models import Appointment, Feedback

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if user.is_patient():
        appointments = Appointment.objects.filter(patient=user).order_by('-created_at')
        context['appointments'] = appointments
        
        # Count appointments by status
        context['pending_count'] = appointments.filter(status='pending').count()
        context['confirmed_count'] = appointments.filter(status='confirmed').count()
        context['completed_count'] = appointments.filter(status='completed').count()
        
    elif user.is_doctor():
        appointments = Appointment.objects.filter(doctor=user).order_by('-created_at')
        context['appointments'] = appointments
        
        # Calculate average rating
        feedbacks = Feedback.objects.filter(appointment__doctor=user)
        if feedbacks.exists():
            context['average_rating'] = feedbacks.aggregate(Avg('rating'))['rating__avg']
        else:
            context['average_rating'] = 0
            
        context['total_appointments'] = appointments.count()
        context['completed_appointments'] = appointments.filter(status='completed').count()
    
    return render(request, 'accounts/dashboard.html', context)