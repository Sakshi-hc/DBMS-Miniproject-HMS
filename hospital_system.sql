-- Drop existing tables if they exist
DROP TABLE IF EXISTS notification;
DROP TABLE IF EXISTS chat_message;
DROP TABLE IF EXISTS bill;
DROP TABLE IF EXISTS medical_record;
DROP TABLE IF EXISTS appointment;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS doctor;
DROP TABLE IF EXISTS patient;
DROP TABLE IF EXISTS user;

-- Create database
CREATE DATABASE IF NOT EXISTS hospital_system;
USE hospital_system;

-- User table
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'staff',
    is_active BOOLEAN DEFAULT TRUE,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Patient table
CREATE TABLE patient (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    blood_group VARCHAR(5),
    address VARCHAR(200),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(120),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    insurance_provider VARCHAR(100),
    insurance_id VARCHAR(50),
    date_registered DATE DEFAULT (CURRENT_DATE()),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Doctor table
CREATE TABLE doctor (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(200) NOT NULL,
    experience_years INT,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    consultation_fee FLOAT NOT NULL,
    availability VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Staff table
CREATE TABLE staff (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    position VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    date_hired DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Appointment table
CREATE TABLE appointment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    purpose VARCHAR(200),
    status VARCHAR(20) DEFAULT 'scheduled',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctor(id) ON DELETE CASCADE
);

-- Medical Record table
CREATE TABLE medical_record (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    record_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    diagnosis TEXT,
    treatment TEXT,
    medications TEXT,
    notes TEXT,
    follow_up_date DATE,
    FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctor(id) ON DELETE CASCADE
);

-- Bill table
CREATE TABLE bill (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    bill_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    doctor_fee FLOAT DEFAULT 0.0,
    medication_charges FLOAT DEFAULT 0.0,
    room_charges FLOAT DEFAULT 0.0,
    lab_test_charges FLOAT DEFAULT 0.0,
    other_charges FLOAT DEFAULT 0.0,
    discount FLOAT DEFAULT 0.0,
    total_amount FLOAT NOT NULL,
    paid_amount FLOAT DEFAULT 0.0,
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    description TEXT,
    FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
);

-- Chat Message table
CREATE TABLE chat_message (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    message TEXT NOT NULL,
    is_bot BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE SET NULL
);

-- Notification table
CREATE TABLE notification (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);