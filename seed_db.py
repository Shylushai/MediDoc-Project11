import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def seed_db():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # Clear existing data (if needed)
    cursor.execute('DELETE FROM Users')
    cursor.execute('DELETE FROM Patients')
    cursor.execute('DELETE FROM Doctors')
    cursor.execute('DELETE FROM Appointments')

    # Insert test user (doctor)
    cursor.execute('''
    INSERT INTO Users (username, password, role) VALUES (?, ?, ?)
    ''', ('doctor1', bcrypt.generate_password_hash('password').decode('utf-8'), 'doctor'))

    # Insert test patients
    cursor.execute('''
    INSERT INTO Patients (name, dob, age, gender, contact) VALUES (?, ?, ?, ?, ?)
    ''', ('Patient A', '1990-01-01', 30, 'Male', '1234567890'))
    
    cursor.execute('''
    INSERT INTO Patients (name, dob, age, gender, contact) VALUES (?, ?, ?, ?, ?)
    ''', ('Patient B', '1985-02-02', 35, 'Female', '0987654321'))

    # Insert test doctor
    cursor.execute('''
    INSERT INTO Doctors (name, specialty, contact) VALUES (?, ?, ?)
    ''', ('Dr. Smith', 'Cardiology', '1112223333'))

    # Insert test appointments
    cursor.execute('''
    INSERT INTO Appointments (patient_id, doctor_id, date, time, reason, status) VALUES (?, ?, ?, ?, ?, ?)
    ''', (1, 1, '2024-06-10', '10:00 AM', 'Checkup', 'Pending'))
    
    cursor.execute('''
    INSERT INTO Appointments (patient_id, doctor_id, date, time, reason, status) VALUES (?, ?, ?, ?, ?, ?)
    ''', (2, 1, '2024-06-11', '11:00 AM', 'Consultation', 'Confirmed'))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_db()
