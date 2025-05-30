from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from hospital_management_system.models import Patient, Doctor, Appointment, Bill
from datetime import datetime, timedelta, date

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['doctor', 'admin']:
            flash('You need doctor privileges to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_age(born):
    """Calculate age from date of birth"""
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def get_dashboard_stats():
    """Get statistics for dashboard"""
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)
    
    stats = {
        'total_patients': Patient.query.count(),
        'total_doctors': Doctor.query.count(),
        'total_appointments': Appointment.query.count(),
        'today_appointments': Appointment.query.filter_by(appointment_date=today).count(),
        'pending_bills': Bill.query.filter_by(payment_status='pending').count(),
        'new_patients': Patient.query.filter(Patient.date_registered >= one_month_ago).count(),
        'completed_appointments': Appointment.query.filter_by(status='completed').count(),
        'monthly_revenue': sum([bill.total_amount for bill in Bill.query.filter(Bill.bill_date >= one_month_ago).all()]),
    }
    
    return stats

def generate_appointment_slots(doctor_id, date):
    """Generate available appointment slots for a doctor on a specific date"""
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return []
    
    # Parse availability - This would need to be implemented based on how availability is stored
    # For this example, let's assume doctors work from 9 AM to 5 PM with 30-minute slots
    slots = []
    start_time = datetime.strptime('09:00', '%H:%M').time()
    end_time = datetime.strptime('17:00', '%H:%M').time()
    
    current_time = datetime.combine(date, start_time)
    end_datetime = datetime.combine(date, end_time)
    
    slot_duration = timedelta(minutes=30)
    
    while current_time < end_datetime:
        time_slot = current_time.time()
        
        # Check if slot is already booked
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=date,
            appointment_time=time_slot
        ).first()
        
        if not existing_appointment:
            slots.append({
                'time': time_slot.strftime('%H:%M'),
                'available': True
            })
        
        current_time += slot_duration
    
    return slots
