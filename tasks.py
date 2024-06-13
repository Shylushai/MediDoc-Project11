import os
import sqlite3
from datetime import datetime, timedelta
import logging

from gmail import send_gmail_notification
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()


def notification_job():
    send_reminders()


def find_appointments_next_24_hours(cursor):
    """
  Fetches appointments scheduled within the next 24 hours from the database.

  Args:
      cursor (sqlite3.Cursor): A database cursor object.

  Returns:
      list: A list of appointment dictionaries containing details from the database.
  """

    current_datetime = datetime.now()  # current time
    tomorrow_datetime = current_datetime + timedelta(days=1)  # current time + 24hr

    # Ensure consistent datetime format (avoid potential truncation)
    current_datetime_formatted = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    tomorrow_datetime_formatted = tomorrow_datetime.strftime('%Y-%m-%d %H:%M:%S')

    query = """
    SELECT *
    FROM Appointments
    WHERE (date || ' ' || time) >= ?
      AND (date || ' ' || time) < ?
      AND status = 'Confirmed'
    """
    print(query)
    cursor.execute(query, (current_datetime_formatted, tomorrow_datetime_formatted))
    appointments = cursor.fetchall()

    return appointments


def print_appointment_details(appointment):
    """
    Prints details of a single appointment.

    Args:
      appointment: A tuple containing appointment details from a database query.
    """

    logging.info("Patient ID: %s", appointment[1])
    logging.info("Doctor ID: %s", appointment[2])
    logging.info("Date: %s", appointment[3])
    logging.info("Time: %s", appointment[4])
    logging.info("Reason: %s", appointment[5])
    logging.info("Status: %s", appointment[6])
    logging.info("----------------------------------------")


def send_reminder(appointment, cursor, conn):
    patient_id = appointment[1]
    doctor_id = appointment[2]
    appointment_date = appointment[3]
    appointment_time = appointment[4]
    reason = appointment[5]
    appointment_id = appointment[0]

    # Fetch patient details
    cursor.execute("SELECT email, name FROM Patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    if not patient:
        logging.warning("No patient found with ID %s", patient_id)
        return
    patient_email = patient[0]
    patient_name = patient[1]

    # Fetch doctor details
    cursor.execute("SELECT name FROM Doctors WHERE id = ?", (doctor_id,))
    doctor = cursor.fetchone()
    if not doctor:
        logging.warning("No doctor found with ID %s", doctor_id)
        return
    doctor_name = doctor[0]

    # Email content
    subject = "Appointment Reminder"
    body = f"Dear {patient_name},\n\nThis is a reminder for your upcoming appointment.\n\n" \
           f"Date: {appointment_date}\nTime: {appointment_time}\nDoctor: Dr. {doctor_name}\n" \
           f"Reason: {reason}\n\nPlease ensure to be on time.\n\nBest regards,\nMediDoc"

    # Send email
    sender_email = os.getenv('SENDER_EMAIL')
    app_password = os.getenv('APP_PASSWORD')
    send_gmail_notification(sender_email, patient_email, app_password, subject, body)

    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO Reminders (appointment_id, patient_id, reminder_sent_at) VALUES (?, ?, ?)",
                   (appointment_id, patient_id, current_datetime))
    conn.commit()
    print("Reminder sent for appointment ID:", appointment_id)


def send_reminders():
    with sqlite3.connect('hospital.db') as conn:  # every data is present in this file
        cursor = conn.cursor()
        appointments = find_appointments_next_24_hours(cursor)  # All appointment
        if appointments:  # it's not empty
            print("Upcoming Appointments (within 24 hours):")
            print("========================================")
            for appointment in appointments:
                reminder_exists = cursor.execute("SELECT * FROM Reminders WHERE appointment_id = ?",
                                                 (appointment[0],)).fetchone()
                if not reminder_exists:  # if appointment is already added in the reminder or not
                    print_appointment_details(appointment)
                    send_reminder(appointment, cursor, conn)  # Call the separate function
            print("Reminders Sent Successfully!")
        else:
            print("No appointments scheduled within the next 24 hours.")
