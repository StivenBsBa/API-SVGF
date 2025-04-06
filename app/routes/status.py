from flask import Blueprint

status_bp = Blueprint("status", __name__)


@status_bp.route("/", methods=["GET"])
def status():
    return {"message": "API funcionando correctamente 🚀"}
