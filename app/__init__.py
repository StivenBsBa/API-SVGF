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


def create_app():
    app = Flask(__name__)

    # 🔹 Cargar variables de entorno desde .env
    load_dotenv()

    # 🔹 Configuración de JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=3)  # tiempo del token

    JWTManager(app)  # Inicializar JWT

    # 🔹 Configurar CORS para permitir solicitudes desde el frontend
    CORS(app, resources={r"/api/*": {"origins": os.getenv("VITE_URL_SVGF")}})

    # 🔹 Registrar Blueprints
    app.register_blueprint(status_bp, url_prefix="/")
    app.register_blueprint(consultas_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(generar_sql_bp, url_prefix="/api")

    return app
