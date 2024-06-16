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
