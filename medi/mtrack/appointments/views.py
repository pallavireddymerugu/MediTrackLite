

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.db.models import Count
from django.db import transaction
from django.utils import timezone
from .models import Appointment, Prescription, Feedback
from .forms import AppointmentForm, PrescriptionForm, FeedbackForm
import datetime

def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role != role:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('accounts:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
@role_required('patient')
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment_date = form.cleaned_data['appointment_date']
            
            # Check if patient already has 2 appointments on the same day
            same_day_appointments = Appointment.objects.filter(
                patient=request.user,
                appointment_date=appointment_date
            ).count()
            
            if same_day_appointments >= 2:
                messages.error(request, 'You cannot book more than 2 appointments on the same day.')
                return render(request, 'appointments/book_appointment.html', {'form': form})
            
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            
            messages.success(request, 'Appointment booked successfully!')
            return redirect('appointments:appointments_list')
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/book_appointment.html', {'form': form})

@login_required
def appointments_list(request):
    if request.user.is_patient():
        appointments = Appointment.objects.filter(patient=request.user).order_by('-created_at')
    else:
        appointments = Appointment.objects.filter(status='pending').order_by('-created_at')
    
    return render(request, 'appointments/appointments_list.html', {'appointments': appointments})

'''@login_required
@role_required('doctor')
def accept_appointment(request, appointment_id):
    with transaction.atomic():
        appointment = get_object_or_404(Appointment, id=appointment_id, status='pending')
        appointment.status = 'confirmed'
        appointment.doctor = request.user
        appointment.save()
        
        messages.success(request, 'Appointment accepted successfully!')
    
    return redirect('appointments:my_appointments')'''
@login_required
@role_required('doctor')
def accept_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, status='pending')
    
    # Check if the current doctor is the assigned doctor for this appointment
    if not (appointment.doctor == request.user or appointment.preferred_doctor == request.user):
        messages.error(request, 'You are not authorized to accept this appointment.')
        return redirect('appointments:my_appointments')
    
    with transaction.atomic():
        appointment.status = 'confirmed'
        appointment.doctor = request.user  # Assign the doctor who accepted
        appointment.save()
        
        messages.success(request, 'Appointment accepted successfully!')
        return redirect('appointments:my_appointments')

@login_required
@role_required('doctor')
def my_appointments(request):
    appointments = Appointment.objects.filter(doctor=request.user).order_by('-created_at')
    return render(request, 'appointments/my_appointments.html', {'appointments': appointments})

@login_required
@role_required('doctor')
def update_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if appointment.can_transition_to(new_status):
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Appointment status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status transition.')
    
    return redirect('appointments:appointment_detail', appointment_id=appointment.id)



@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has permission to view this appointment
    # Allow patient, assigned doctor, or preferred doctor to view
    has_permission = (
        appointment.patient == request.user or 
        appointment.doctor == request.user or 
        appointment.preferred_doctor == request.user
    )
    
    if not has_permission:
        raise Http404("Appointment not found")
    
    prescription = None
    feedback = None
    
    try:
        prescription = appointment.prescription
    except Prescription.DoesNotExist:
        pass
    
    try:
        feedback = appointment.feedback
    except Feedback.DoesNotExist:
        pass
    
    context = {
        'appointment': appointment,
        'prescription': prescription,
        'feedback': feedback,
    }
    
    return render(request, 'appointments/appointment_detail.html', context)

@login_required
@role_required('doctor')
def add_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user, status='completed')
    
    if hasattr(appointment, 'prescription'):
        messages.info(request, 'Prescription already exists for this appointment.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.save()
            messages.success(request, 'Prescription added successfully!')
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    else:
        form = PrescriptionForm()
    
    return render(request, 'appointments/add_prescription.html', {'form': form, 'appointment': appointment})

@login_required
@role_required('patient')
def submit_feedback(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user, status='completed')
    
    if hasattr(appointment, 'feedback'):
        messages.info(request, 'You have already submitted feedback for this appointment.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.appointment = appointment
            feedback.patient = request.user
            feedback.doctor = appointment.doctor
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    else:
        form = FeedbackForm()
    
    return render(request, 'appointments/feedback_form.html', {'form': form, 'appointment': appointment})