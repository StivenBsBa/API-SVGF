from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import bcrypt
from app.config.connection import Database

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Autenticación de usuario y generación de token JWT"""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # ⚠️ Verificar que se envió email y password
    if not email or not password:
        return (
            jsonify({"success": False, "error": "Email y contraseña requeridos"}),
            400,
        )

    conn = None
    cursor = None

    try:
        db = Database()
        conn = db.get_connection()

        # ⚠️ Si no hay conexión, devolver error
        if not conn:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No se pudo conectar a la base de datos",
                    }
                ),
                500,
            )

        cursor = conn.cursor()

        # 🔹 Detectar si es MySQL (incluye IAVEN) o SQL Server
        if db.db_type in ["mysql", "iaven"]:
            query = "SELECT id, email, password_hash FROM usuarios WHERE email = %s"
        else:  # SQL Server
            query = "SELECT id, email, password_hash FROM usuarios WHERE email = ?"

        # ✅ Ejecutar la consulta con el parámetro
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        # ⚠️ Si el usuario no existe, devolver error
        if not user:
            return jsonify({"success": False, "error": "Credenciales incorrectas"}), 401

        # Obtener nombres de columnas
        columns = [column[0] for column in cursor.description]
        user = dict(zip(columns, user))

        # 🔑 Comparar contraseña encriptada
        if not bcrypt.checkpw(
            password.encode("utf-8"), user["password_hash"].encode("utf-8")
        ):
            return jsonify({"success": False, "error": "Credenciales incorrectas"}), 401

        # 🔹 Generar token JWT con duración de 1 hora
        access_token = create_access_token(
            identity={"id": user["id"], "email": user["email"]}
        )

        return jsonify({"success": True, "token": access_token})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        # 🔹 Cerrar cursor y conexión si fueron creados
        if cursor:
            cursor.close()
        if conn:
            conn.close()
