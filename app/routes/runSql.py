from app.config.connection import Database
from flask import Blueprint, request, jsonify

consultas_bp = Blueprint("consultas", __name__)


@consultas_bp.route("/RunSql", methods=["POST"])
def ejecutar_consulta():
    try:
        # Obtener la consulta SQL del cuerpo de la solicitud
        data = request.json
        consulta_sql = data.get("consulta")

        if not consulta_sql:
            return jsonify(
                {"success": False, "error": "No se proporcionó una consulta SQL"}
            )

        # Ejecutar la consulta en la base de datos
        db = Database()
        conexion = db.get_connection()
        cursor = conexion.cursor()
        cursor.execute(consulta_sql)
        resultados = cursor.fetchall()

        # Formatear resultados
        columnas = [col[0] for col in cursor.description]  # Nombres de las columnas
        datos = [
            dict(zip(columnas, fila)) for fila in resultados
        ]  # Datos en formato JSON

        # Cerrar la conexión
        cursor.close()
        conexion.close()

        # Devolver los resultados con un mensaje fijo
        return jsonify(
            {
                "success": True,
                "datos": datos,
                "respuesta": "Aqui esta tu consulta.",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
