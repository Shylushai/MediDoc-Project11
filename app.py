from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from flask_bcrypt import Bcrypt
from tenacity import retry, stop_after_attempt, wait_fixed
import logging
import os
from io import BytesIO
from flask import send_from_directory
import api.v2.endpoint as api
from scheduler import init_scheduler

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'
app.register_blueprint(api.endpoint_v2, url_prefix="/api/v2")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)
logging.basicConfig(level=logging.DEBUG)


# Database connection
def get_db_connection():
    conn = sqlite3.connect('hospital.db')
    conn.row_factory = sqlite3.Row
    return conn


# User loader
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'], role=user['role'])
    return None


class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": "not shown",
            "role": self.role,
        }


# Retry decorator for database operations
@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def execute_query(query, args=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        conn.commit()
        last_id = cursor.lastrowid
    except sqlite3.OperationalError as e:
        logging.error(f"Database operation failed: {e}")
        raise
    finally:
        conn.close()
    return last_id


@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def fetch_query(query, args=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        rows = cursor.fetchall()
        return rows
    except sqlite3.OperationalError as e:
        logging.error(f"Database operation failed: {e}")
        raise
    finally:
        conn.close()

#index route
@app.route('/')
@login_required
def index():
    patients = []
    doctors = []
    appointments = []
    upcoming_reminders = []

    if current_user.role == 'admin':
        patients = fetch_query('SELECT * FROM Patients')
        doctors = fetch_query('SELECT * FROM Doctors')
        appointments = fetch_query('''
            SELECT Appointments.id, Appointments.date, Appointments.time, Appointments.reason, Appointments.status,
                   Patients.first_name as patient_name, Patients.contact as patient_contact
            FROM Appointments
            JOIN Patients ON Appointments.patient_id = Patients.patient_id
            ORDER BY Appointments.date, Appointments.time
        ''')
    elif current_user.role == 'patient':
        doctors = fetch_query('SELECT * FROM Doctors')
        appointments = fetch_query('''
            SELECT Appointments.id, Appointments.date, Appointments.time, Appointments.reason, Appointments.status,
                   Patients.first_name as patient_name, Patients.contact as patient_contact
            FROM Appointments
            JOIN Patients ON Appointments.patient_id = Patients.patient_id
            WHERE Appointments.patient_id = ?
            ORDER BY Appointments.date, Appointments.time
        ''', (current_user.id,))
        reminders = fetch_query('''
            SELECT a.*, r.reminder_sent_at FROM Appointments a JOIN Reminders r ON a.id =
            r.appointment_id WHERE a.patient_id = ? AND r.seen_in_ui = 0
        ''', (current_user.id,))
        for reminder in reminders:
            formatted_date = datetime.strptime(reminder['date'], '%Y-%m-%d').strftime('%d-%b-%Y')
            reminder_data = {
                'appointment_id': reminder['id'],
                'date': formatted_date + ' ' + reminder['time'],
                'message': reminder['reason'],
                'reminder_sent_at': reminder['reminder_sent_at']
            }
            upcoming_reminders.append(reminder_data)
    elif current_user.role == 'doctor':
        appointments = fetch_query('''
            SELECT Appointments.id, Appointments.date, Appointments.time, Appointments.reason, Appointments.status,
                   Patients.first_name as patient_name, Patients.contact as patient_contact
            FROM Appointments
            JOIN Patients ON Appointments.patient_id = Patients.patient_id
            WHERE Appointments.doctor_id = ?
            ORDER BY Appointments.date, Appointments.time
        ''', (current_user.id,))
    elif current_user.role == 'receptionist':
        doctors = fetch_query('SELECT * FROM Doctors')
        appointments = fetch_query('''
            SELECT Appointments.id, Appointments.date, Appointments.time, Appointments.reason, Appointments.status,
                   Patients.first_name as patient_name, Patients.contact as patient_contact
            FROM Appointments
            JOIN Patients ON Appointments.patient_id = Patients.patient_id
            ORDER BY Appointments.date, Appointments.time
        ''')

    return render_template('index.html', patients=patients, doctors=doctors, appointments=appointments,
                           upcoming_reminders=upcoming_reminders)

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(id=user['id'], username=user['username'], password=user['password'], role=user['role'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

#logout function
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        role = request.form['role']
        try:
            execute_query('INSERT INTO Users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
            if role == 'patient':
                name = request.form.get('name')
                dob = request.form.get('dob')
                age = request.form.get('age')
                gender = request.form.get('gender')
                contact = request.form.get('contact')
                email = request.form.get('email')
                execute_query(
                    '''INSERT INTO Patients (name, dob, age, gender, contact, email) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (name, dob, age, gender, contact, email)
                )
            flash('Registration successful, please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'error')
    return render_template('register.html')

#admin_setup route
@app.route('/admin_setup', methods=['GET', 'POST'])
@login_required
def admin_setup():
    global department_id
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    suggested_times = [
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM",
        "11:30 AM", "12:00 PM", "12:30 PM", "01:00 PM", "01:30 PM",
        "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
        "04:30 PM", "05:00 PM"
    ]

    if request.method == 'POST':
        try:
            # Handle adding department
            if 'department_name' in request.form:
                department_name = request.form['department_name'].strip()
                if department_name:
                    logging.debug(f"Adding department: {department_name}")
                    department_id = execute_query('INSERT INTO Departments (name) VALUES (?)', (department_name,))

            # Handle adding doctor
            if 'doctor_name' in request.form:
                doctor_name = request.form['doctor_name'].strip()
                specialty = request.form['specialty'].strip()
                contact = request.form['contact'].strip()
                if doctor_name and specialty and contact:
                    logging.debug(f"Adding doctor: {doctor_name}, {specialty}, {contact}")
                    execute_query('INSERT INTO Doctors (name, specialty, contact, department_id) VALUES (?, ?, ?, ?)',
                                  (doctor_name, specialty, contact, department_id))

            # Handle setting time slots
            if 'time_slots_select' in request.form:
                selected_slots = request.form.getlist('time_slots')
                logging.debug(f"Setting time slots: {selected_slots}")
                execute_query('DELETE FROM AvailableTimeSlots')
                for slot in selected_slots:
                    execute_query('INSERT INTO AvailableTimeSlots (time) VALUES (?)', (slot,))

            return redirect(url_for('admin_setup'))

        except sqlite3.IntegrityError as e:
            logging.error(f"Database integrity error: {e}")
            flash(
                'An integrity error occurred while processing your request. Please ensure that no duplicate entries are made.',
                'error')
        except sqlite3.OperationalError as e:
            logging.error(f"Database operational error: {e}")
            flash('A database error occurred while processing your request. Please try again.', 'error')

    departments = fetch_query('SELECT * FROM Departments')

    return render_template('admin_setup.html', suggested_times=suggested_times, departments=departments)

#delete patient function
@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    if current_user.role != 'admin':
        return redirect(url_for('unorthorised'))
    execute_query('DELETE FROM Patients WHERE patient_id = ?', (patient_id,))
    return redirect(url_for('index'))

#delte doctor function
@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    if current_user.role != 'admin':
        return redirect(url_for('unorthorised'))
    execute_query('DELETE FROM Doctors WHERE doctor_id = ?', (doctor_id,))
    return redirect(url_for('index'))

#delete appointment function
@app.route('/delete_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    if current_user.role != 'admin':
        return redirect(url_for('unorthorised'))
    execute_query('DELETE FROM Appointments WHERE id = ?', (appointment_id,))
    return redirect(url_for('index'))

#bookappointment route
@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        patient_id = current_user.id
        patient_name = request.form['patient_name']
        contact = request.form['contact']
        email = request.form['email']
        doctor_id = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        reason = request.form['reason'] if request.form['reason'] else 'No message provided'
        execute_query(
            'INSERT INTO Appointments (patient_id, doctor_id, date, time, reason, status) VALUES (?, ?, ?, ?, ?, ?)',
            (patient_id, doctor_id, date, time, reason, 'Pending'))
        flash('Appointment booked successfully', 'success')
        return redirect(url_for('index'))
    departments = fetch_query('SELECT * FROM Departments')
    doctors = fetch_query('SELECT * FROM Doctors')
    available_slots = fetch_query('SELECT * FROM AvailableTimeSlots')
    return render_template('book_appointment.html', departments=departments, doctors=doctors,
                           available_slots=available_slots)

#manage appointment route
@app.route('/manage_appointments', methods=['POST'])
@login_required
def manage_appointments():
    if current_user.role != 'admin':
        return redirect(url_for('unorthorised'))

    appointment_id = request.form['appointment_id']
    action = request.form['action']

    if action == 'confirm':
        execute_query('UPDATE Appointments SET status = ? WHERE id = ?', ('Confirmed', appointment_id))
    elif action == 'decline':
        execute_query('UPDATE Appointments SET status = ? WHERE id = ?', ('Declined', appointment_id))

    return redirect(url_for('index'))

#user mangement route
@app.route('/user_management', methods=['GET', 'POST'])
@login_required
def user_management():
    if current_user.role != 'admin':
        return redirect(url_for('unorthorised'))

    if request.method == 'POST':
        user_id = request.form['user_id']
        if 'change_role' in request.form:
            new_role = request.form['new_role']
            execute_query('UPDATE Users SET role = ? WHERE id = ?', (new_role, user_id))
        elif 'delete_user' in request.form:
            execute_query('DELETE FROM Users WHERE id = ?', (user_id,))
        return redirect(url_for('user_management'))

    users = fetch_query('SELECT * FROM Users')

    return render_template('user_management.html', users=users)

#update patient function
@app.route('/update_patient', methods=['GET', 'POST'])
@login_required
def update_patient():
    if current_user.role != 'patient':
        return redirect(url_for('unorthorised'))

    if request.method == 'POST':
        # Patient information
        patient_id = request.form['patient_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']
        dob = request.form['dob']
        
        # Emergency contact information
        sub_first_name = request.form['sub_first_name']
        sub_last_name = request.form['sub_last_name']
        sub_relationship = request.form['sub_relationship']
        sub_address = request.form['sub_address']
        sub_email = request.form['sub_email']
        sub_contact = request.form['sub_contact']

        execute_query(  """
        UPDATE Patients
        SET first_name = ?, last_name = ?, email = ?, contact = ?, address = ?, dob = ?
        WHERE patient_id = ?
        """,
            (
                first_name,
                last_name,
                email,
                contact,
                address,
                dob,
                patient_id,
            ))
        execute_query(
            """
        UPDATE EmergencyContact
        SET first_name = ?, last_name = ?, email = ?, contact = ?, address = ?, relationship = ?
        WHERE patient_id = ?
        """,
            (sub_first_name, sub_last_name, sub_email, sub_contact, sub_address, sub_relationship, patient_id),
        )
        flash('Information updated successfully', 'success')
        return redirect(url_for('index'))

    patient = fetch_query('SELECT * FROM Patients WHERE user_id = ?', (current_user.id,))
    if patient:
        patient = patient[0]
        print(patient)
        emergency_contact = fetch_query('SELECT * FROM EmergencyContact WHERE patient_id = ?', (patient['patient_id'],))
        emergency_contact = emergency_contact[0]

    return render_template('update_patient.html', patient=patient, emergency_contact=emergency_contact)

#book appointment route and function
@app.route('/receptionist_book_appointment', methods=['GET', 'POST'])
@login_required
def receptionist_book_appointment():
    if current_user.role != 'receptionist':
        return redirect(url_for('unorthorised'))

    if request.method == 'POST':
        patient_name = request.form['patient_name']
        patient = fetch_query('SELECT * FROM Patients WHERE name = ?', (patient_name,))
        if not patient:
            flash('Patient not found', 'danger')
            return redirect(url_for('receptionist_book_appointment'))

        patient_id = patient[0]['id']
        doctor_id = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        reason = request.form['reason'] if request.form['reason'] else 'No message provided'
        execute_query('INSERT INTO Appointments (patient_id, doctor_id, date, time, reason, status) VALUES (?, ?, ?, ?, ?, ?)',
                      (patient_id, doctor_id, date, time, reason, 'Pending'))
        flash('Appointment booked successfully', 'success')
        return redirect(url_for('index'))

    doctors = fetch_query('SELECT * FROM Doctors')
    available_slots = fetch_query('SELECT * FROM AvailableTimeSlots')
    return render_template('receptionist_book_appointment.html', doctors=doctors, available_slots=available_slots)

#search patient route and function
@app.route('/search_patient', methods=['GET', 'POST'])
@login_required
def search_patient():
    if current_user.role != 'receptionist':
        return redirect(url_for('unorthorised'))

    patients = []
    if request.method == 'POST' and 'search_term' in request.form:
        search_term = request.form['search_term']
        patients = fetch_query('SELECT * FROM Patients WHERE name LIKE ?', ('%' + search_term + '%',))

        # Store the search history
        execute_query('INSERT INTO SearchHistory (receptionist_id, patient_name) VALUES (?, ?)',
                      (current_user.id, search_term))

    # Fetch search history
    search_history = fetch_query('SELECT * FROM SearchHistory WHERE receptionist_id = ? ORDER BY search_time DESC',
                                 (current_user.id,))

    return render_template('search_patient.html', patients=patients, search_history=search_history)

#delete history function
@app.route('/delete_search_history/<int:history_id>', methods=['POST'])
@login_required
def delete_search_history(history_id):
    if current_user.role != 'receptionist':
        return redirect(url_for('unorthorised'))

    execute_query('DELETE FROM SearchHistory WHERE id = ?', (history_id,))
    return redirect(url_for('search_patient'))

#clear history function
@app.route('/clear_search_history', methods=['POST'])
@login_required
def clear_search_history():
    if current_user.role != 'receptionist':
        return redirect(url_for('unorthorised'))

    execute_query('DELETE FROM SearchHistory WHERE receptionist_id = ?', (current_user.id,))
    return redirect(url_for('search_patient'))

#doctor search route
@app.route('/doctor_patient_search', methods=['GET', 'POST'])
@login_required
def doctor_patient_search():
    users = fetch_query('SELECT * FROM Users')
    patients = fetch_query('SELECT * FROM Users WHERE role = \'patient\'')
    return render_template('Doctor_patient_search.html', users=users, patients=patients)

#doctor search function
@app.route('/doctor_search', methods=['GET', 'POST'])
@login_required
def doctor_search():
    name = request.form['searchName']
    users = fetch_query('SELECT * FROM Users')
    patients = fetch_query('SELECT * FROM Users WHERE role = \'patient\' AND username LIKE ?', ('%' + name + '%',))
    return render_template('Doctor_patient_search.html', users=users, patients=patients)

#upload route
@app.route('/upload', methods=['POST'])
def upload():
    if current_user.role != 'doctor':
        return redirect(url_for('unorthorised'))
    id = request.form['id']
    file = request.files['file']
    users = fetch_query('SELECT * FROM Users')
    patients = fetch_query('SELECT * FROM Users WHERE role = \'patient\'')
    try:
        os.mkdir('uploads/{value}'.format(value=id))
    except OSError:
        print("Creation of the directory failed")
    else:
        print("Successfully created the directory")
    files = os.listdir('uploads/{value}'.format(value=id))
    if file:
        file.save(f'uploads/{id}/{file.filename}')
    return render_template('Doctor_patient_search.html', users=users, files=files, patients=patients)

#download function
@app.route('/download/<int:id>', methods=['GET'])
@login_required
def download(id):
    if current_user.role != 'doctor':
        return redirect(url_for('unorthorised'))
    id = id
    try:
        os.mkdir('uploads/{value}'.format(value=id))
    except OSError:
        print("Creation of the directory failed")
    else:
        print("Successfully created the directory")
    users = fetch_query('SELECT * FROM Users')
    files = os.listdir('uploads/{value}'.format(value=id))

    return render_template('download.html', users=users, files=files, id=id)

#document download function
@app.route('/document_download/<int:id>/<string:file_name>', methods=['GET'])
@login_required
def document_download(id, file_name):
    if current_user.role != 'doctor':
        return redirect(url_for('unorthorised'))
    file = file_name
    print(file)
    users = fetch_query('SELECT * FROM Users')
    return send_from_directory('uploads/{value}'.format(value=id), file, as_attachment=True)

#reminders function
@app.route('/api/mark_reminders_seen', methods=['POST'])
def mark_reminders_seen():
    patient_id = request.json.get('patient_id')
    if patient_id:
        update_reminder_seen_status(patient_id)
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400


def update_reminder_seen_status(patient_id):
    # Your database query to mark reminders as seen for the given patient_id
    query = "UPDATE Reminders SET seen_in_ui = 1 WHERE patient_id = ? AND seen_in_ui = 0"
    execute_query(query, (patient_id,))

#recetpionist confirm appointment function
@app.route('/confirm_appointment', methods=['GET', 'POST'])
@login_required
def confirm_appointment():
    if current_user.role != 'receptionist':
        return redirect(url_for('unorthorised'))
    if request.method == 'POST':
        id = request.form['appointment_id']
        execute_query("UPDATE Appointments SET status = 'Confirmed' WHERE id = {value}".format(value=id))
        print('works')
        return redirect(url_for('index'))
    print('no')
    return redirect(url_for('index'))

#receptionist deny appointment function
@app.route('/deny_appointment', methods=['GET', 'POST'])
@login_required
def deny_appointment():
    if current_user.role != 'receptionist':
        return redirect(url_for('unorthorised'))
    if request.method == 'POST':
        id = request.form['appointment_id']
        execute_query('DELETE FROM Appointments WHERE id = {value}'.format(value=id))
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/unorthorised', methods=['GET', 'POST'])
@login_required
def unorthorised():

    return render_template('unorthorised.html')

if __name__ == '__main__':
    init_scheduler(app)
    app.run(debug=True, port=5001)
