from audioop import add
from math import e
from flask_cors import CORS, cross_origin
from flask_login import login_user
from flask import Blueprint, Flask, request, jsonify
from utils.general import convert_records_to_dicts, init_db_connection
from flask_bcrypt import Bcrypt

bp = Blueprint("patient", __name__, url_prefix="/patient")
bcrypt = Bcrypt()


# Get Patient Basic Info
@bp.route("/", methods=["GET", "POST"])
def patient_get_basic_info():
    if request.method == "GET":
        patient_id = request.args.get("patient_id")
        # user_id = request.form.get("user_id")
        cn = init_db_connection()
        cursor = cn.cursor()
        cursor.execute(
            "SELECT * FROM Users Join Patients On Users.id = Patients.user_id WHERE Patients.patient_id = ?",
            (patient_id,),
        )
        user = cursor.fetchone()
        user_dict = {
            description[0]: value
            for description, value in zip(cursor.description, user)
        }
        user_dict.pop("password")

        cursor.execute(
            "SELECT * FROM EmergencyContact WHERE patient_id = ?",
            (patient_id,),
        )
        user = cursor.fetchone()
        sub_contact_dict = {
            description[0]: value
            for description, value in zip(cursor.description, user)
        }

        cn.close()

        return jsonify({"user": user_dict, "emergency_contact": sub_contact_dict})
    elif request.method == "POST":
        print(request.get_json())
        data = request.get_json()
        patient_id = data["user"]["patient_id"]
        first_name = data["user"]["first_name"]
        last_name = data["user"]["last_name"]
        email = data["user"]["email"]
        contact = data["user"]["contact"]
        address = data["user"]["address"]
        dob = data["user"]["dob"]

        cn = init_db_connection()
        cursor = cn.cursor()

        cursor.execute(
            """
        UPDATE Patients
        SET first_name = ?, last_name = ?, email = ?, contact = ?, address = ?, dob = ?
        WHERE patient_id = ?
        """,
            (first_name, last_name, email, contact, address, dob, patient_id),
        )
        
        cursor.execute(
            """
        UPDATE EmergencyContact
        SET first_name = ?, last_name = ?, email = ?, contact = ?, address = ?
        WHERE patient_id = ?
        """,
            (first_name, last_name, email, contact, address, patient_id),
        )
        
        cn.commit()
        cn.close()

        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error"})


# Update Patient Basic Info
# @bp.put("/")
# def patient_update_basic_info():
#     print(request)
#     patient_id = request.form.get("patient_id")
#     first_name = request.form.get("first_name")
#     last_name = request.form.get("last_name")

#     print(f"Patient ID: {patient_id}")
#     print(f"First Name: {first_name}")
#     print(f"Last Name: {last_name}")

#     cn = init_db_connection()
#     cursor = cn.cursor()

#     return jsonify({"status": "success"})


# Get Patient Record
@bp.route("/get_record", methods=["GET"])
def patient_get_record():
    patient_id = request.args.get("patient_id")
    # patient_id = request.form.get("patient_id")
    cn = init_db_connection()
    cursor = cn.cursor()
    # Allergy
    cursor.execute(
        "SELECT * FROM Allergy WHERE Allergy.patient_id = ?",
        (patient_id,),
    )
    records = cursor.fetchall()

    allergy_list = convert_records_to_dicts(cursor, records)

    # Document
    cursor.execute(
        "SELECT * FROM Document WHERE Document.patient_id = ?",
        (patient_id,),
    )
    records = cursor.fetchall()
    document_list = convert_records_to_dicts(cursor, records)

    # Immunisation
    cursor.execute(
        "SELECT * FROM Immunisation WHERE Immunisation.patient_id = ?",
        (patient_id,),
    )
    records = cursor.fetchall()
    immunisation_list = convert_records_to_dicts(cursor, records)

    # Medicine
    cursor.execute(
        "SELECT * FROM Medicine WHERE Medicine.patient_id = ?",
        (patient_id,),
    )
    records = cursor.fetchall()
    medicine_list = convert_records_to_dicts(cursor, records)

    # Test Results
    cursor.execute(
        "SELECT * FROM TestResult WHERE TestResult.patient_id = ?",
        (patient_id,),
    )
    records = cursor.fetchall()
    testresult_list = convert_records_to_dicts(cursor, records)

    cn.close()

    result = {
        "allergy": allergy_list,
        "document": document_list,
        "immunisation": immunisation_list,
        "medicine": medicine_list,
        "testresult": testresult_list,
    }

    return jsonify(result)
