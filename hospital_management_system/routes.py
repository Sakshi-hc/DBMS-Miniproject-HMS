import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from hospital_management_system.extensions import db
from hospital_management_system.models import User, Patient, Doctor, Staff, Appointment, MedicalRecord, Bill
from hospital_management_system.forms import (LoginForm, RegistrationForm, PatientForm, DoctorForm, StaffForm,
                   AppointmentForm, MedicalRecordForm, BillForm, PatientRegistrationForm)
from hospital_management_system.utils import admin_required, doctor_required, get_dashboard_stats, generate_appointment_slots
from hospital_management_system.notifications import Notification
from hospital_management_system.chatbot import Chatbot, ChatMessage

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('main', __name__)

# Auth routes
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {e}")
            flash('An error occurred while creating the account.', 'danger')
    
    return render_template('register.html', form=form)

@bp.route('/register/patient', methods=['GET', 'POST'])
def register_patient():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = PatientRegistrationForm()
    if form.validate_on_submit():
        # Create user account
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='patient'
        )
        user.set_password(form.password.data)
        
        # Create patient profile
        patient = Patient(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            phone=form.phone.data,
            address=form.address.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            user=user
        )
        
        try:
            db.session.add(user)
            db.session.add(patient)
            db.session.commit()
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during patient registration: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register_patient.html', form=form)

# Dashboard
@bp.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    
    # Get recent appointments and patients for quick access
    recent_appointments = (Appointment.query
                          .filter(Appointment.appointment_date >= datetime.now().date())
                          .order_by(Appointment.appointment_date, Appointment.appointment_time)
                          .limit(5)
                          .all())
    
    recent_patients = (Patient.query
                      .order_by(Patient.date_registered.desc())
                      .limit(5)
                      .all())
    
    return render_template('dashboard.html', 
                          stats=stats, 
                          recent_appointments=recent_appointments, 
                          recent_patients=recent_patients)

# Patient routes
@bp.route('/patients')
@login_required
def patients():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = Patient.query
    if search:
        query = query.filter(
            (Patient.first_name.ilike(f'%{search}%')) |
            (Patient.last_name.ilike(f'%{search}%')) |
            (Patient.phone.ilike(f'%{search}%')) |
            (Patient.email.ilike(f'%{search}%'))
        )
    
    patients = query.order_by(Patient.last_name).paginate(page=page, per_page=10)
    return render_template('patients/index.html', patients=patients, search=search)

@bp.route('/patients/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        # Create user account first
        user = User(
            username=form.email.data,  # Using email as username
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='patient'
        )
        user.set_password('default123')  # Set a default password
        
        # Create patient profile
        patient = Patient(
            user=user,  # This will set the user_id
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            blood_group=form.blood_group.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            insurance_provider=form.insurance_provider.data,
            insurance_id=form.insurance_id.data
        )
        
        try:
            db.session.add(user)
            db.session.add(patient)
            db.session.commit()
            flash('Patient added successfully!', 'success')
            return redirect(url_for('patients'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding patient: {e}")
            flash('An error occurred while adding the patient.', 'danger')
    
    return render_template('patients/add.html', form=form)

@bp.route('/patients/<int:id>')
@login_required
def view_patient(id):
    patient = Patient.query.get_or_404(id)
    appointments = Appointment.query.filter_by(patient_id=id).order_by(Appointment.appointment_date.desc()).all()
    medical_records = MedicalRecord.query.filter_by(patient_id=id).order_by(MedicalRecord.record_date.desc()).all()
    bills = Bill.query.filter_by(patient_id=id).order_by(Bill.bill_date.desc()).all()
    
    return render_template('patients/view.html', 
                          patient=patient, 
                          appointments=appointments, 
                          medical_records=medical_records, 
                          bills=bills)

@bp.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    form = PatientForm(obj=patient)
    
    if form.validate_on_submit():
        form.populate_obj(patient)
        
        try:
            db.session.commit()
            flash('Patient updated successfully!', 'success')
            return redirect(url_for('view_patient', id=patient.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating patient: {e}")
            flash('An error occurred while updating the patient.', 'danger')
    
    return render_template('patients/edit.html', form=form, patient=patient)

@bp.route('/patients/<int:id>/delete')
@admin_required
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    try:
        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting patient: {e}")
        flash('An error occurred while deleting the patient.', 'danger')
    return redirect(url_for('main.patients'))

# Doctor routes
@bp.route('/doctors')
@login_required
def doctors():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = Doctor.query.join(User)
    if search:
        query = query.filter(
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%')) |
            (Doctor.specialization.ilike(f'%{search}%'))
        )
    
    doctors = query.order_by(User.last_name).paginate(page=page, per_page=10)
    return render_template('doctors/index.html', doctors=doctors, search=search)

@bp.route('/doctors/add', methods=['GET', 'POST'])
@admin_required
def add_doctor():
    form = DoctorForm()
    form.user_id.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.username})") 
                          for u in User.query.filter_by(role='doctor').all()]
    
    if form.validate_on_submit():
        doctor = Doctor(
            user_id=form.user_id.data,
            specialization=form.specialization.data,
            qualification=form.qualification.data,
            experience_years=form.experience_years.data,
            license_number=form.license_number.data,
            consultation_fee=form.consultation_fee.data,
            availability=form.availability.data
        )
        
        try:
            db.session.add(doctor)
            db.session.commit()
            flash('Doctor profile added successfully!', 'success')
            return redirect(url_for('doctors'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding doctor: {e}")
            flash('An error occurred while adding the doctor profile.', 'danger')
    
    return render_template('doctors/add.html', form=form)

@bp.route('/doctors/<int:id>')
@login_required
def view_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    appointments = Appointment.query.filter_by(doctor_id=id).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctors/view.html', doctor=doctor, appointments=appointments)

@bp.route('/doctors/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    form = DoctorForm(obj=doctor)
    form.user_id.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.username})") 
                          for u in User.query.filter_by(role='doctor').all()]
    
    if form.validate_on_submit():
        form.populate_obj(doctor)
        
        try:
            db.session.commit()
            flash('Doctor profile updated successfully!', 'success')
            return redirect(url_for('view_doctor', id=doctor.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating doctor: {e}")
            flash('An error occurred while updating the doctor profile.', 'danger')
    
    return render_template('doctors/edit.html', form=form, doctor=doctor)

@bp.route('/doctors/<int:id>/delete')
@admin_required
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    try:
        db.session.delete(doctor)
        db.session.commit()
        flash('Doctor deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting doctor: {e}")
        flash('An error occurred while deleting the doctor.', 'danger')
    return redirect(url_for('main.doctors'))

# Staff routes
@bp.route('/staff')
@admin_required
def staff():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = Staff.query.join(User)
    if search:
        query = query.filter(
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%')) |
            (Staff.position.ilike(f'%{search}%')) |
            (Staff.department.ilike(f'%{search}%'))
        )
    
    staff = query.order_by(User.last_name).paginate(page=page, per_page=10)
    return render_template('staff/index.html', staff=staff, search=search)

@bp.route('/staff/add', methods=['GET', 'POST'])
@admin_required
def add_staff():
    form = StaffForm()
    form.user_id.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.username})") 
                          for u in User.query.filter_by(role='staff').all()]
    
    if form.validate_on_submit():
        staff = Staff(
            user_id=form.user_id.data,
            position=form.position.data,
            department=form.department.data,
            date_hired=form.date_hired.data
        )
        
        try:
            db.session.add(staff)
            db.session.commit()
            flash('Staff profile added successfully!', 'success')
            return redirect(url_for('staff'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding staff: {e}")
            flash('An error occurred while adding the staff profile.', 'danger')
    
    return render_template('staff/add.html', form=form)

# Appointment routes
@bp.route('/appointments')
@login_required
def appointments():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    date = request.args.get('date', '')
    page = request.args.get('page', 1, type=int)
    
    query = Appointment.query.join(Patient).join(Doctor).join(User, Doctor.user_id == User.id)
    
    if search:
        query = query.filter(
            (Patient.first_name.ilike(f'%{search}%')) |
            (Patient.last_name.ilike(f'%{search}%')) |
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%'))
        )
    
    if status:
        query = query.filter(Appointment.status == status)
    
    if date:
        try:
            appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
            query = query.filter(Appointment.appointment_date == appointment_date)
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'warning')
    
    # If current user is a doctor, show only their appointments
    if current_user.role == 'doctor' and hasattr(current_user, 'doctor_profile'):
        query = query.filter(Appointment.doctor_id == current_user.doctor_profile.id)
    
    appointments = query.order_by(Appointment.appointment_date, Appointment.appointment_time).paginate(page=page, per_page=10)
    return render_template('appointments/index.html', appointments=appointments, search=search, status=status, date=date)

@bp.route('/appointments/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    form = AppointmentForm()
    form.patient_id.choices = [(p.id, f"{p.first_name} {p.last_name}") for p in Patient.query.order_by(Patient.last_name).all()]
    
    # If current user is a doctor, pre-select them
    if current_user.role == 'doctor' and hasattr(current_user, 'doctor_profile'):
        doctors = [(current_user.doctor_profile.id, f"{current_user.first_name} {current_user.last_name} - {current_user.doctor_profile.specialization}")]
    else:
        doctors = [(d.id, f"{d.user.first_name} {d.user.last_name} - {d.specialization}") for d in Doctor.query.join(User).order_by(User.last_name).all()]
    
    form.doctor_id.choices = doctors
    
    if form.validate_on_submit():
        appointment = Appointment(
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
            purpose=form.purpose.data,
            status=form.status.data,
            notes=form.notes.data
        )
        
        try:
            db.session.add(appointment)
            db.session.commit()
            flash('Appointment scheduled successfully!', 'success')
            return redirect(url_for('appointments'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error scheduling appointment: {e}")
            flash('An error occurred while scheduling the appointment.', 'danger')
    
    return render_template('appointments/add.html', form=form)

@bp.route('/appointments/<int:id>')
@login_required
def view_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    return render_template('appointments/view.html', appointment=appointment)

@bp.route('/appointments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    # Security check: only admin, assigned doctor, or staff can edit
    if (current_user.role != 'admin' and 
        (current_user.role == 'doctor' and 
         current_user.doctor_profile and 
         current_user.doctor_profile.id != appointment.doctor_id)):
        flash('You do not have permission to edit this appointment.', 'danger')
        return redirect(url_for('appointments'))
    
    form = AppointmentForm(obj=appointment)
    form.patient_id.choices = [(p.id, f"{p.first_name} {p.last_name}") for p in Patient.query.order_by(Patient.last_name).all()]
    
    # If current user is a doctor, pre-select them
    if current_user.role == 'doctor' and hasattr(current_user, 'doctor_profile'):
        doctors = [(current_user.doctor_profile.id, f"{current_user.first_name} {current_user.last_name} - {current_user.doctor_profile.specialization}")]
    else:
        doctors = [(d.id, f"{d.user.first_name} {d.user.last_name} - {d.specialization}") for d in Doctor.query.join(User).order_by(User.last_name).all()]
    
    form.doctor_id.choices = doctors
    
    if form.validate_on_submit():
        form.populate_obj(appointment)
        
        try:
            db.session.commit()
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('view_appointment', id=appointment.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating appointment: {e}")
            flash('An error occurred while updating the appointment.', 'danger')
    
    return render_template('appointments/edit.html', form=form, appointment=appointment)

@bp.route('/appointments/<int:id>/delete')
@login_required
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting appointment: {e}")
        flash('An error occurred while deleting the appointment.', 'danger')
    return redirect(url_for('main.appointments'))

@bp.route('/appointments/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = 'canceled'
    db.session.commit()
    flash('Appointment canceled.', 'info')
    return redirect(url_for('main.appointments'))

# Medical Record routes
@bp.route('/medical-records')
@login_required
def medical_records():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = MedicalRecord.query.join(Patient).join(Doctor).join(User, Doctor.user_id == User.id)
    
    if search:
        query = query.filter(
            (Patient.first_name.ilike(f'%{search}%')) |
            (Patient.last_name.ilike(f'%{search}%')) |
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%')) |
            (MedicalRecord.diagnosis.ilike(f'%{search}%'))
        )
    
    # If current user is a doctor, show only their medical records
    if current_user.role == 'doctor' and hasattr(current_user, 'doctor_profile'):
        query = query.filter(MedicalRecord.doctor_id == current_user.doctor_profile.id)
    
    records = query.order_by(MedicalRecord.record_date.desc()).paginate(page=page, per_page=10)
    return render_template('medical_records/index.html', records=records, search=search)

@bp.route('/medical-records/add', methods=['GET', 'POST'])
@doctor_required
def add_medical_record():
    form = MedicalRecordForm()
    form.patient_id.choices = [(p.id, f"{p.first_name} {p.last_name}") for p in Patient.query.order_by(Patient.last_name).all()]
    
    # If current user is a doctor, pre-select them
    if current_user.role == 'doctor' and hasattr(current_user, 'doctor_profile'):
        doctors = [(current_user.doctor_profile.id, f"{current_user.first_name} {current_user.last_name}")]
    else:
        doctors = [(d.id, f"{d.user.first_name} {d.user.last_name}") for d in Doctor.query.join(User).order_by(User.last_name).all()]
    
    form.doctor_id.choices = doctors
    
    # Pre-populate patient_id if coming from patient view
    patient_id = request.args.get('patient_id', type=int)
    if patient_id:
        form.patient_id.data = patient_id
    
    if form.validate_on_submit():
        record = MedicalRecord(
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            diagnosis=form.diagnosis.data,
            treatment=form.treatment.data,
            medications=form.medications.data,
            notes=form.notes.data,
            follow_up_date=form.follow_up_date.data
        )
        
        try:
            db.session.add(record)
            db.session.commit()
            flash('Medical record added successfully!', 'success')
            return redirect(url_for('view_patient', id=form.patient_id.data))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding medical record: {e}")
            flash('An error occurred while adding the medical record.', 'danger')
    
    return render_template('medical_records/add.html', form=form)

@bp.route('/medical-records/<int:id>')
@login_required
def view_medical_record(id):
    record = MedicalRecord.query.get_or_404(id)
    return render_template('medical_records/view.html', record=record)

@bp.route('/medical-records/<int:id>/edit', methods=['GET', 'POST'])
@doctor_required
def edit_medical_record(id):
    record = MedicalRecord.query.get_or_404(id)
    
    # Security check: only admin or the doctor who created the record can edit it
    if (current_user.role != 'admin' and 
        (current_user.role == 'doctor' and 
         current_user.doctor_profile and 
         current_user.doctor_profile.id != record.doctor_id)):
        flash('You do not have permission to edit this medical record.', 'danger')
        return redirect(url_for('medical_records'))
    
    form = MedicalRecordForm(obj=record)
    form.patient_id.choices = [(p.id, f"{p.first_name} {p.last_name}") for p in Patient.query.order_by(Patient.last_name).all()]
    
    # If current user is a doctor, pre-select them
    if current_user.role == 'doctor' and hasattr(current_user, 'doctor_profile'):
        doctors = [(current_user.doctor_profile.id, f"{current_user.first_name} {current_user.last_name}")]
    else:
        doctors = [(d.id, f"{d.user.first_name} {d.user.last_name}") for d in Doctor.query.join(User).order_by(User.last_name).all()]
    
    form.doctor_id.choices = doctors
    
    if form.validate_on_submit():
        form.populate_obj(record)
        
        try:
            db.session.commit()
            flash('Medical record updated successfully!', 'success')
            return redirect(url_for('view_medical_record', id=record.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating medical record: {e}")
            flash('An error occurred while updating the medical record.', 'danger')
    
    return render_template('medical_records/edit.html', form=form, record=record)

@bp.route('/medical-records/<int:id>/delete')
@doctor_required
def delete_medical_record(id):
    record = MedicalRecord.query.get_or_404(id)
    try:
        db.session.delete(record)
        db.session.commit()
        flash('Medical record deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting medical record: {e}")
        flash('An error occurred while deleting the medical record.', 'danger')
    return redirect(url_for('main.medical_records'))

# Billing routes
@bp.route('/billing')
@login_required
def billing():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    query = Bill.query.join(Patient)
    
    if search:
        query = query.filter(
            (Patient.first_name.ilike(f'%{search}%')) |
            (Patient.last_name.ilike(f'%{search}%')) |
            (Patient.phone.ilike(f'%{search}%'))
        )
    
    if status:
        query = query.filter(Bill.payment_status == status)
    
    bills = query.order_by(Bill.bill_date.desc()).paginate(page=page, per_page=10)
    return render_template('billing/index.html', bills=bills, search=search, status=status)

@bp.route('/billing/add', methods=['GET', 'POST'])
@login_required
def add_bill():
    form = BillForm()
    form.patient_id.choices = [(p.id, f"{p.first_name} {p.last_name}") for p in Patient.query.order_by(Patient.last_name).all()]
    
    # Pre-populate patient_id if coming from patient view
    patient_id = request.args.get('patient_id', type=int)
    if patient_id:
        form.patient_id.data = patient_id
    
    if form.validate_on_submit():
        bill = Bill(
            patient_id=form.patient_id.data,
            doctor_fee=form.doctor_fee.data,
            medication_charges=form.medication_charges.data,
            room_charges=form.room_charges.data,
            lab_test_charges=form.lab_test_charges.data,
            other_charges=form.other_charges.data,
            discount=form.discount.data,
            total_amount=form.total_amount.data,
            paid_amount=form.paid_amount.data,
            payment_status=form.payment_status.data,
            payment_method=form.payment_method.data,
            description=form.description.data
        )
        
        try:
            db.session.add(bill)
            db.session.commit()
            flash('Bill added successfully!', 'success')
            return redirect(url_for('main.view_patient', id=form.patient_id.data))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding bill: {e}")
            flash('An error occurred while adding the bill.', 'danger')
    
    return render_template('billing/add.html', form=form)

@bp.route('/billing/<int:id>')
@login_required
def view_bill(id):
    bill = Bill.query.get_or_404(id)
    return render_template('billing/view.html', bill=bill)

@bp.route('/billing/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bill(id):
    bill = Bill.query.get_or_404(id)
    form = BillForm(obj=bill)
    form.patient_id.choices = [(p.id, f"{p.first_name} {p.last_name}") for p in Patient.query.order_by(Patient.last_name).all()]
    
    if form.validate_on_submit():
        form.populate_obj(bill)
        
        try:
            db.session.commit()
            flash('Bill updated successfully!', 'success')
            return redirect(url_for('main.view_bill', id=bill.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating bill: {e}")
            flash('An error occurred while updating the bill.', 'danger')
    
    return render_template('billing/edit.html', form=form, bill=bill)

@bp.route('/billing/<int:id>/delete')
@admin_required
def delete_bill(id):
    bill = Bill.query.get_or_404(id)
    try:
        db.session.delete(bill)
        db.session.commit()
        flash('Bill deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting bill: {e}")
        flash('An error occurred while deleting the bill.', 'danger')
    return redirect(url_for('main.billing'))

# Admin routes
@bp.route('/admin')
@admin_required
def admin():
    return render_template('admin/index.html')

@bp.route('/admin/users')
@admin_required
def admin_users():
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    page = request.args.get('page', 1, type=int)
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.order_by(User.last_name).paginate(page=page, per_page=10)
    return render_template('admin/users.html', users=users, search=search, role=role)

# API routes for AJAX
@bp.route('/api/appointment-slots')
@login_required
def get_appointment_slots():
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date')
    
    if not doctor_id or not date_str:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        slots = generate_appointment_slots(doctor_id, date_obj)
        return jsonify({'slots': slots})
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except Exception as e:
        logger.error(f"Error generating appointment slots: {e}")
        return jsonify({'error': 'Server error'}), 500

# Notification routes
@bp.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    notifications = (Notification.query
                    .filter_by(user_id=current_user.id)
                    .order_by(Notification.created_at.desc())
                    .paginate(page=page, per_page=10))
    return render_template('notifications/index.html', notifications=notifications)

@bp.route('/notifications/mark_read/<int:id>')
@login_required
def mark_notification_read(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('notifications'))
    
    notification.mark_as_read()
    return redirect(url_for('notifications'))

@bp.route('/notifications/mark_all_read')
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications'))

# Chatbot routes
@bp.route('/chat')
@login_required
def chat():
    # Get chat history
    messages = (ChatMessage.query
                .filter(
                    (ChatMessage.user_id == current_user.id) | 
                    (ChatMessage.user_id.is_(None) & ChatMessage.is_bot.is_(True))
                )
                .order_by(ChatMessage.created_at.desc())
                .limit(50)
                .all())
    messages.reverse()  # Show oldest messages first
    return render_template('chat/index.html', messages=messages)

@bp.route('/chat/send', methods=['POST'])
@login_required
def send_message():
    message = request.form.get('message')
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get bot response
    response = Chatbot.get_response(message, current_user.id)
    
    return jsonify({
        'status': 'success',
        'response': response
    })
