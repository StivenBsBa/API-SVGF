from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta
import os

# Importar Blueprints
from app.routes.runSql import consultas_bp
from app.routes.status import status_bp
from app.routes.login import auth_bp
from app.routes.genimi import generar_sql_bp

# Importar conexión DB
from app.config.connection import Database  # Asegúrate que esta ruta sea correcta

def create_app():
    app = Flask(__name__)

    # 🔹 Cargar variables de entorno desde .env
    load_dotenv()

    # 🔹 Configuración de JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=3)

    JWTManager(app)

    # 🔹 Configurar CORS
    app_origin = os.getenv("VITE_URL_SVGF", "*")
    CORS(app, resources={r"/api/*": {"origins": app_origin}})

    # 🔹 Registrar Blueprints
    app.register_blueprint(status_bp, url_prefix="/")
    app.register_blueprint(consultas_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(generar_sql_bp, url_prefix="/api")

    # 🔹 Verificar conexión a la base de datos al primer request
    @app.before_request
    def verificar_conexion():
        if not hasattr(app, 'db_checked'):
            try:
                db = Database()
                connection = db.get_connection()

                if connection:
                    print("✅ Conexión exitosa a la base de datos")
                    connection.close()
                else:
                    print("❌ Error al conectar a la base de datos")

                app.db_checked = True

            except Exception as e:
                print(f"❌ Error al conectar a la base de datos: {e}")

    return app
