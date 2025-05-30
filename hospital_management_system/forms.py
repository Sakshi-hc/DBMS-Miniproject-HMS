from datetime import date, datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TimeField
from wtforms import TextAreaField, FloatField, IntegerField, BooleanField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from hospital_management_system.models import User, Patient, Doctor

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('staff', 'Staff'), ('doctor', 'Doctor'), ('admin', 'Admin')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')

class PatientRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    emergency_contact_name = StringField('Emergency Contact Name', validators=[DataRequired()])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class PatientForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('other', 'Other')
    ], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Unknown'), 
        ('A+', 'A+'), 
        ('A-', 'A-'), 
        ('B+', 'B+'), 
        ('B-', 'B-'), 
        ('AB+', 'AB+'), 
        ('AB-', 'AB-'), 
        ('O+', 'O+'), 
        ('O-', 'O-')
    ])
    address = StringField('Address', validators=[Length(max=200)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    email = EmailField('Email', validators=[Optional(), Email(), Length(max=120)])
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Length(max=100)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Length(max=20)])
    insurance_provider = StringField('Insurance Provider', validators=[Length(max=100)])
    insurance_id = StringField('Insurance ID', validators=[Length(max=50)])
    medical_history = TextAreaField('Medical History', validators=[Optional(), Length(max=500)])
    allergies = TextAreaField('Allergies', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Submit')
    
    def validate_date_of_birth(self, field):
        if field.data > date.today():
            raise ValidationError('Date of birth cannot be in the future.')

class DoctorForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(max=100)])
    qualification = StringField('Qualification', validators=[DataRequired(), Length(max=200)])
    experience_years = IntegerField('Years of Experience', validators=[DataRequired()])
    license_number = StringField('License Number', validators=[DataRequired(), Length(max=50)])
    consultation_fee = FloatField('Consultation Fee', validators=[DataRequired()])
    availability = TextAreaField('Availability', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    def validate_license_number(self, license_number):
        doctor = Doctor.query.filter_by(license_number=license_number.data).first()
        if doctor and doctor.id != self.id.data:
            raise ValidationError('This license number is already registered.')

class StaffForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired(), Length(max=100)])
    department = StringField('Department', validators=[DataRequired(), Length(max=100)])
    date_hired = DateField('Date Hired', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    def validate_date_hired(self, field):
        if field.data > date.today():
            raise ValidationError('Hire date cannot be in the future.')

class AppointmentForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Appointment Date', validators=[DataRequired()])
    appointment_time = TimeField('Appointment Time', validators=[DataRequired()])
    purpose = StringField('Purpose', validators=[Length(max=200)])
    status = SelectField('Status', choices=[
        ('scheduled', 'Scheduled'), 
        ('completed', 'Completed'), 
        ('canceled', 'Canceled'), 
        ('no-show', 'No Show')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')
    
    def validate_appointment_date(self, field):
        if field.data < date.today():
            raise ValidationError('Appointment date cannot be in the past.')

class MedicalRecordForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired()])
    treatment = TextAreaField('Treatment', validators=[DataRequired()])
    medications = TextAreaField('Medications')
    notes = TextAreaField('Notes')
    follow_up_date = DateField('Follow-up Date', validators=[Optional()])
    submit = SubmitField('Submit')

class BillForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    doctor_fee = FloatField('Doctor Fee', default=0.0)
    medication_charges = FloatField('Medication Charges', default=0.0)
    room_charges = FloatField('Room Charges', default=0.0)
    lab_test_charges = FloatField('Lab Test Charges', default=0.0)
    other_charges = FloatField('Other Charges', default=0.0)
    discount = FloatField('Discount', default=0.0)
    total_amount = FloatField('Total Amount', validators=[DataRequired()])
    paid_amount = FloatField('Paid Amount', default=0.0)
    payment_status = SelectField('Payment Status', choices=[
        ('pending', 'Pending'), 
        ('partial', 'Partial'), 
        ('paid', 'Paid')
    ], validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('', 'Not Selected'),
        ('cash', 'Cash'), 
        ('credit_card', 'Credit Card'), 
        ('debit_card', 'Debit Card'), 
        ('insurance', 'Insurance'), 
        ('online', 'Online Payment')
    ])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')
    
    def validate_paid_amount(self, field):
        if field.data > self.total_amount.data:
            raise ValidationError('Paid amount cannot be greater than total amount.')
