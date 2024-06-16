from flask_login import login_user
from flask import Blueprint, json, request, jsonify
from utils.general import (
    convert_records_to_dicts,
    convert_single_record_to_dict,
    init_db_connection,
)
from flask_bcrypt import Bcrypt

bp = Blueprint("restore_db", __name__, url_prefix="/admin/restore_db")
bcrypt = Bcrypt()


@bp.route("/", methods=["POST"])
def restore_db_post():
    from app import User

    print("Start Restore DB")
    data = request.get_json()
    target = request.args.get("target")

    cn = init_db_connection()
    cursor = cn.cursor()

    if target == "Users":
        for record in data:
            hashed_password = bcrypt.generate_password_hash(record["password"]).decode(
                "utf-8"
            )
            cursor.execute(
                "INSERT INTO Users (id, username, password, role) VALUES (?, ?, ?, ?)",
                (
                    record["id"],
                    record["username"],
                    hashed_password,
                    record["role"],
                ),
            )
            print("loaded user data", record)
    elif target == "Patients":
        for record in data:
            cursor.execute(
                "INSERT INTO Patients (patient_id, user_id, first_name, last_name, email, contact, address, dob, gender,age) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["patient_id"],
                    record["user_id"],
                    record["first_name"],
                    record["last_name"],
                    record["email"],
                    record["contact"],
                    record["address"],
                    record["dob"],
                    record["gender"],
                    record["age"],
                ),
            )
            print("loaded patient data", record)
    elif target == "Allergy":
        for record in data:
            cursor.execute(
                "INSERT INTO Allergy (allergy_id, patient_id, allergen_name, severity, reaction, diagnosis_date, treatment, allergist_name, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["allergy_id"],
                    record["patient_id"],
                    record["allergen_name"],
                    record["severity"],
                    record["reaction"],
                    record["diagnosis_date"],
                    record["treatment"],
                    record["allergist_name"],
                    record["notes"],
                ),
            )
            print("loaded allergy data", record)
    elif target == "Immunisation":
        for record in data:
            cursor.execute(
                "INSERT INTO Immunisation (immunisation_id, patient_id, vaccine_name, vaccine_dose, vaccination_date, vaccination_location, vaccinator_name, vaccination_status, side_effects, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["immunisation_id"],
                    record["patient_id"],
                    record["vaccine_name"],
                    record["vaccine_dose"],
                    record["vaccination_date"],
                    record["vaccination_location"],
                    record["vaccinator_name"],
                    record["vaccination_status"],
                    record["side_effects"],
                    record["notes"],
                ),
            )
            print("loaded immunisation data", record)
    elif target == "Medicine":
        for record in data:
            cursor.execute(
                "INSERT INTO Medicine (medicine_id, patient_id, diagnosis_code, diagnosis, prescription_date, medication_name, dosage_amount, dosage_unit, frequency, prescribing_doctor, start_date, end_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["medicine_id"],
                    record["patient_id"],
                    record["diagnosis_code"],
                    record["diagnosis"],
                    record["prescription_date"],
                    record["medication_name"],
                    record["dosage_amount"],
                    record["dosage_unit"],
                    record["frequency"],
                    record["prescribing_doctor"],
                    record["start_date"],
                    record["end_date"],
                    record["notes"],
                ),
            )
            print("loaded medicine data", record)
    elif target == "TestResult":
        for record in data:
            cursor.execute(
                "INSERT INTO TestResult (testresult_id, patient_id, test_name, test_date, result_value, unit, normal_range, doctor_name, hospital_name, lab_technician, comments, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["testresult_id"],
                    record["patient_id"],
                    record["test_name"],
                    record["test_date"],
                    record["result_value"],
                    record["unit"],
                    record["normal_range"],
                    record["doctor_name"],
                    record["hospital_name"],
                    record["lab_technician"],
                    record["comments"],
                    record["notes"],
                ),
            )
            print("loaded test result data", record)
    elif target == "EmergencyContact":
        for record in data:
            cursor.execute(
                "INSERT INTO EmergencyContact (emergency_contact_id, patient_id, first_name, last_name, relationship, address, email, contact, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["emergency_contact_id"],
                    record["patient_id"],
                    record["first_name"],
                    record["last_name"],
                    record["relationship"],
                    record["address"],
                    record["email"],
                    record["contact"],
                    record["notes"],
                ),
            )
            print("loaded emergency contact data", record)
    elif target == "Document":
        for record in data:
            cursor.execute(
                "INSERT INTO Document (document_id, patient_id, document_title, document_type, document_format, document_url, creation_date, author_name, file_size, document_keywords) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["document_id"],
                    record["patient_id"],
                    record["document_title"],
                    record["document_type"],
                    record["document_format"],
                    record["document_url"],
                    record["creation_date"],
                    record["author_name"],
                    record["file_size"],
                    record["document_keywords"],
                ),
            )
            print("loaded document data", record)
    elif target == "Doctors":
        for record in data:
            cursor.execute(
                "INSERT INTO Doctors (doctor_id, user_id, first_name, last_name, specialty, contact, email, department_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["doctor_id"],
                    record["user_id"],
                    record["first_name"],
                    record["last_name"],
                    record["specialty"],
                    record["contact"],
                    record["email"],
                    record["department_id"],
                ),
            )
            print("loaded doctor data", record)

    cn.commit()
    cn.close()

    return jsonify({"status": "success"})


@bp.route("/patient", methods=["POST"])
def login_as_patient_post():
    from app import User

    username = request.form.get("username")
    password = request.form.get("password")
    cn = init_db_connection()
    cursor = cn.cursor()
    cursor.execute(
        "SELECT * FROM Users Join Patients On Users.id = Patients.user_id WHERE username = ?",
        (username,),
    )
    user = cursor.fetchone()
    cn.close()
    if user and bcrypt.check_password_hash(user["password"], password):
        user_obj = User(
            id=user["id"],
            username=user["username"],
            password=user["password"],
            role=user["role"],
        )
        login_user(user_obj)
        result = convert_single_record_to_dict(cursor, user)
        result.pop("password")
        # result = {"username": user["username"], "role": user["role"]}
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid username or password"}), 401
