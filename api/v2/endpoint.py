from flask import Blueprint
import api.v2.login
import api.v2.patient
import api.v2.restore_db

endpoint_v2 = Blueprint("v2", __name__)
endpoint_v2.register_blueprint(api.v2.login.bp)
endpoint_v2.register_blueprint(api.v2.patient.bp)
endpoint_v2.register_blueprint(api.v2.restore_db.bp)