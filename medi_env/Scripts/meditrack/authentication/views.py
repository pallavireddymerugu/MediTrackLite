
# authentication/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistrationForm, LoginForm
from .models import User
from django.contrib.auth import authenticate, login as auth_login

def home(request):
    """Public home page"""
    return render(request, 'authentication/home.html')

class RegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please log in.')
        return response

def login_view(request):
    """Custom login view"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})

@login_required
def dashboard(request):
    """Role-based dashboard"""
    user = request.user
    
    if user.is_patient():
        return render(request, 'authentication/patient_dashboard.html', {'user': user})
    elif user.is_doctor():
        return render(request, 'authentication/doctor_dashboard.html', {'user': user})
    else:
        return render(request, 'authentication/dashboard.html', {'user': user})

@login_required
def patient_only_view(request):
    """View accessible only to patients"""
    if not request.user.is_patient():
        messages.error(request, 'Access denied. Patients only.')
        return redirect('dashboard')
    
    return render(request, 'authentication/patient_only.html')

@login_required
def doctor_only_view(request):
    """View accessible only to doctors"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('dashboard')
    
    return render(request, 'authentication/doctor_only.html')

def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')
