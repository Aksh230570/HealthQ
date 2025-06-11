import sqlite3

conn = sqlite3.connect('doctor.db')
cursor = conn.cursor()

# Drop existing tables
cursor.execute('DROP TABLE IF EXISTS doctors')
cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('DROP TABLE IF EXISTS appointments')
cursor.execute('DROP TABLE IF EXISTS time_slots')

# Doctors Table
cursor.execute('''
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    qualifications TEXT,
    experience INTEGER,
    rating REAL,
    patients INTEGER,
    location TEXT,
    hospital TEXT,
    overall_rating INTEGER,
    address TEXT,
    consultation_fee INTEGER,
    speciality TEXT
)
''')

# Users Table (for Patients)
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    blood_group TEXT,
    dob TEXT,
    medical_history TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Appointments Table
cursor.execute('''
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER,
    doctor_name TEXT,
    doctor_hospital TEXT,
    patient_name TEXT,
    patient_email TEXT,           
    patient_phone TEXT,
    appointment_date TEXT,
    appointment_time TEXT,
    status TEXT DEFAULT 'Confirmed'
)
''')

# Time Slots Table
cursor.execute('''
CREATE TABLE time_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER,
    slot_time TEXT,
    is_available BOOLEAN
)
''')

print("All Tables Created Successfully ✅")

conn.commit()
conn.close()
