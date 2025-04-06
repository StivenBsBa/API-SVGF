import os
from flask import Blueprint, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
from app.config.connection import Database  # Importa la clase de conexión a la BD

# Cargar variables de entorno
load_dotenv()

# Obtener la clave API desde el archivo .env
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("No se encontró la clave API. Verifica tu archivo .env.")

# Configurar la API de Gemini
genai.configure(api_key=API_KEY)
modelo = genai.GenerativeModel("gemini-1.5-pro")

# Definir la estructura de la base de datos
estructura_bd = """
La base de datos contiene tablas relacionadas con finanzas:
- departamentos(id, nombre, descripcion)
- categorias_gastos(id, nombre, descripcion)
- cuentas(id, nombre, saldo_inicial, saldo_actual, moneda)
- proveedores(id, nombre, nit, direccion, telefono)
- presupuestos(id, nombre, monto, fecha_inicio, fecha_fin, departamento_id, categoria_id)
- gastos(id, fecha, monto, descripcion, categoria_id, departamento_id, cuenta_id, proveedor_id)

Relaciones:
- presupuestos.departamento_id -> departamentos.id
- presupuestos.categoria_id -> categorias_gastos.id
- gastos.departamento_id -> departamentos.id
- gastos.categoria_id -> categorias_gastos.id
- gastos.cuenta_id -> cuentas.id
- gastos.proveedor_id -> proveedores.id

Cuando te pase una pregunta en lenguaje natural, solo responde con la consulta SQL. 
Si la pregunta no está relacionada con finanzas, presupuestos o gastos, responde con "NO_RELEVANTE".
"""

# Crear Blueprint
generar_sql_bp = Blueprint("generar_sql", __name__)


@generar_sql_bp.route("/generar_sql", methods=["POST"])
def generar_y_ejecutar_sql():
    try:
        # Obtener la pregunta en lenguaje natural del request
        data = request.json
        pregunta = data.get("pregunta")

        if not pregunta:
            return jsonify({"success": False, "error": "Se requiere una pregunta"}), 400

        # Generar la consulta SQL usando la API de Gemini
        prompt = f"{estructura_bd}\n\nPregunta: {pregunta}\n\nConsulta SQL:"
        respuesta = modelo.generate_content(prompt)

        consulta_sql = (
            respuesta.text.strip().replace("```sql", "").replace("```", "").strip()
            if respuesta and hasattr(respuesta, "text")
            else None
        )

        # Validar si la IA no puede responder
        if not consulta_sql or "NO_RELEVANTE" in consulta_sql:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Solo puedo responder preguntas relacionadas con finanzas, presupuestos o gastos.",
                    }
                ),
                400,
            )

        # Verificar que la consulta sea segura (solo SELECT)
        palabras_prohibidas = ["drop", "delete", "insert", "update", "alter"]
        if any(palabra in consulta_sql.lower() for palabra in palabras_prohibidas):
            return (
                jsonify({"success": False, "error": "Consulta SQL no permitida."}),
                403,
            )

        if not consulta_sql.lower().startswith("select"):
            return (
                jsonify(
                    {"success": False, "error": "Solo se permiten consultas SELECT"}
                ),
                403,
            )

        # Conectar a la base de datos y ejecutar la consulta
        db = Database()
        conexion = db.get_connection()

        if not conexion:
            return (
                jsonify(
                    {"success": False, "error": "Error de conexión a la base de datos"}
                ),
                500,
            )

        cursor = conexion.cursor()
        cursor.execute(consulta_sql)
        resultados = cursor.fetchall()

        # Formatear resultados
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, fila)) for fila in resultados]

        # Generar respuesta en lenguaje natural
        respuesta_texto = modelo.generate_content(
            f"""
    Actúa como un asistente experto en bases de datos. 
    Un usuario ha realizado la siguiente pregunta sobre la base de datos:

    Pregunta del usuario:
    "{pregunta}"

    La base de datos tiene la siguiente estructura:
    {estructura_bd}

    Genera una respuesta clara y concisa en lenguaje natural, explicando lo que representa la consulta sin incluir código SQL.
    Inicia la respuesta con "Aquí tienes la información que encontré:" y luego proporciona la respuesta detallada.
    """
        )

        respuesta_final = (
            respuesta_texto.text.strip()
            if respuesta_texto
            and hasattr(respuesta_texto, "text")
            and respuesta_texto.text
            else "Aquí están los resultados de la consulta."
        )

        return jsonify(
            {
                "consulta_sql": consulta_sql,
                "respuesta": respuesta_final,
                "datos": datos,
                "success": True,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if "cursor" in locals() and cursor is not None:
            cursor.close()
        if "conexion" in locals() and conexion is not None:
            conexion.close()
