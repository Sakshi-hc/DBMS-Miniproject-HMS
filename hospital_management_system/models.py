from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

# db and login_manager will be initialized in app.py and imported here

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')  # admin, doctor, staff, patient
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Define relationships
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade="all, delete-orphan")
    staff_profile = db.relationship('Staff', backref='user', uselist=False, cascade="all, delete-orphan")
    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.username}>'

class Patient(db.Model):
    __tablename__ = 'patient'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    insurance_provider = db.Column(db.String(100))
    insurance_id = db.Column(db.String(50))
    date_registered = db.Column(db.Date, default=date.today)
    
    # Define relationships
    appointments = db.relationship('Appointment', backref='patient', cascade="all, delete-orphan")
    medical_records = db.relationship('MedicalRecord', backref='patient', cascade="all, delete-orphan")
    bills = db.relationship('Bill', backref='patient', cascade="all, delete-orphan")
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'

class Doctor(db.Model):
    __tablename__ = 'doctor'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(200), nullable=False)
    experience_years = db.Column(db.Integer)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    consultation_fee = db.Column(db.Float, nullable=False)
    availability = db.Column(db.String(255))  # Stored as serialized JSON or text representation
    
    # Define relationships
    appointments = db.relationship('Appointment', backref='doctor', cascade="all, delete-orphan")
    medical_records = db.relationship('MedicalRecord', backref='doctor', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Doctor {self.id} - {self.specialization}>'

class Staff(db.Model):
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    date_hired = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f'<Staff {self.id} - {self.position}>'

class Appointment(db.Model):
    __tablename__ = 'appointment'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    purpose = db.Column(db.String(200))
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, canceled, no-show
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.appointment_date}>'

class MedicalRecord(db.Model):
    __tablename__ = 'medical_record'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    medications = db.Column(db.Text)
    notes = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    
    def __repr__(self):
        return f'<MedicalRecord {self.id} - {self.record_date}>'

class Bill(db.Model):
    __tablename__ = 'bill'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    bill_date = db.Column(db.DateTime, default=datetime.utcnow)
    doctor_fee = db.Column(db.Float, default=0.0)
    medication_charges = db.Column(db.Float, default=0.0)
    room_charges = db.Column(db.Float, default=0.0)
    lab_test_charges = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid
    payment_method = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    @property
    def balance(self):
        return self.total_amount - self.paid_amount
    
    def __repr__(self):
        return f'<Bill {self.id} - {self.bill_date}>'