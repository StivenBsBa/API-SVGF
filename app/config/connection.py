import os
import mysql.connector
import pyodbc
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Database:
    def __init__(self):
        self.db_type = os.getenv("DB_TYPE", "mysql").lower()  # "mysql" o "sqlserver"

        if self.db_type == "mysql":
            self.config = {
                "user": os.getenv("MYSQL_USER"),
                "password": os.getenv("MYSQL_PASSWORD"),
                "host": os.getenv("MYSQL_HOST"),
                "database": os.getenv("MYSQL_DATABASE"),
                "raise_on_warnings": os.getenv(
                    "MYSQL_RAISE_ON_WARNINGS", "True"
                ).lower()
                == "true",
            }
        elif self.db_type == "sqlserver":
            self.config = {
                "DRIVER": os.getenv(
                    "VITE_DB_DRIVER", "{ODBC Driver 18 for SQL Server}"
                ),
                "SERVER": os.getenv("VITE_DB_SERVER"),
                "DATABASE": os.getenv("VITE_DB_NAME"),
                "UID": os.getenv("VITE_DB_USER"),
                "PWD": os.getenv("VITE_DB_PASSWORD"),
                "Encrypt": os.getenv("VITE_DB_ENCRYPT", "yes"),
                "TrustServerCertificate": os.getenv("VITE_DB_TRUST_CERTIFICATE", "no"),
                "Connection Timeout": os.getenv("VITE_DB_TIMEOUT", "30"),
            }
        else:
            raise ValueError("DB_TYPE no es válido. Usa 'mysql' o 'sqlserver'.")

    def get_connection(self):
        """Retorna una conexión a la base de datos seleccionada y muestra a cuál se está conectando."""
        try:
            if self.db_type == "mysql":
                conn = mysql.connector.connect(**self.config)
                print(
                    f"✅ Conectado a MySQL: {self.config['database']} en {self.config['host']}"
                )
            elif self.db_type == "sqlserver":
                conn_str = ";".join([f"{k}={v}" for k, v in self.config.items()])
                conn = pyodbc.connect(conn_str)
                print(
                    f"✅ Conectado a SQL Server: {self.config['DATABASE']} en {self.config['SERVER']}"
                )
            return conn
        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")
            return None


# 🔹 Prueba la conexión
if __name__ == "__main__":
    db = Database()
    conn = db.get_connection()

    if conn:
        try:
            cursor = conn.cursor()
            if db.db_type == "mysql":
                cursor.execute("SELECT VERSION()")  # Consulta en MySQL
            else:
                cursor.execute("SELECT @@VERSION")  # Consulta en SQL Server

            print("📌 Versión de la base de datos:", cursor.fetchone()[0])
        except Exception as e:
            print(f"❌ Error al ejecutar la consulta: {e}")
        finally:
            cursor.close()
            conn.close()
