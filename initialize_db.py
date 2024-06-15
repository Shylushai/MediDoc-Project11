import sqlite3


def initialize_db():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS Departments')
    cursor.execute('DROP TABLE IF EXISTS Doctors')
    cursor.execute('DROP TABLE IF EXISTS AvailableTimeSlots')
    cursor.execute('DROP TABLE IF EXISTS Patients')
    cursor.execute('DROP TABLE IF EXISTS Appointments')
    cursor.execute('DROP TABLE IF EXISTS Users')
    cursor.execute('DROP TABLE IF EXISTS Reminders')

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')

    # Create Patients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Patients (
        id INTEGER,
        name TEXT NOT NULL,
        dob DATE NOT NULL,
        age INTEGER NOT NULL,
        email TEXT NOT NULL,
        gender TEXT NOT NULL,
        contact TEXT NOT NULL
    )
    ''')

    # Create Doctors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        contact TEXT NOT NULL,
        department_id INTEGER NOT NULL,
        FOREIGN KEY(department_id) REFERENCES Departments(id)
    )
    ''')

    # Create Appointments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        date DATE NOT NULL,
        time TEXT NOT NULL,
        reason TEXT,
        status TEXT NOT NULL,
        FOREIGN KEY(patient_id) REFERENCES Patients(id),
        FOREIGN KEY(doctor_id) REFERENCES Doctors(id)
    )
    ''')

    # Create Departments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    # Create AvailableTimeSlots table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AvailableTimeSlots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT NOT NULL UNIQUE
    )
    ''')

    # Create SearchHistory table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SearchHistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receptionist_id INTEGER NOT NULL,
        patient_name TEXT NOT NULL,
        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(receptionist_id) REFERENCES Users(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        reminder_sent_at TEXT NOT NULL,
        seen_in_ui BOOLEAN DEFAULT 0
     )
     ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_db()
