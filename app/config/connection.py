import os
import mysql.connector
import pyodbc
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Database:
    def __init__(self):
        self.db_type = os.getenv(
            "DB_TYPE", "mysql"
        ).lower()  # "mysql", "sqlserver" o "iaven"

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

        elif self.db_type == "iaven":
            self.config = {
                "user": os.getenv("IAVEN_USER"),
                "password": os.getenv("IAVEN_PASSWORD"),
                "host": os.getenv("IAVEN_HOST"),
                "port": int(os.getenv("IAVEN_PORT", 3306)),
                "database": os.getenv("IAVEN_DATABASE"),
            }
        else:
            raise ValueError(
                "DB_TYPE no es válido. Usa 'mysql', 'sqlserver' o 'iaven'."
            )

    def get_connection(self, retries=5, delay=3):
        """Reintentar conexión."""
        attempt = 0
        while attempt < retries:
            try:
                if self.db_type == "mysql" or self.db_type == "iaven":
                    conn = mysql.connector.connect(**self.config)
                    print(
                        f"✅ Conectado a {'IAVEN' if self.db_type == 'iaven' else 'MySQL'}: {self.config['database']} en {self.config['host']}:{self.config.get('port', 3306)}"
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
                attempt += 1
                if attempt < retries:
                    print(f"⏳ Intentando de nuevo... ({attempt}/{retries})")
                    time.sleep(delay)
                else:
                    print("❌ Se agotaron los intentos de conexión.")
                    return None


# 🔹 Prueba la conexión
if __name__ == "__main__":
    db = Database()
    conn = db.get_connection()

    if conn:
        try:
            cursor = conn.cursor()
            if db.db_type in ["mysql", "iaven"]:
                cursor.execute("SELECT VERSION()")
            else:
                cursor.execute("SELECT @@VERSION")

            print("📌 Versión de la base de datos:", cursor.fetchone()[0])
        except Exception as e:
            print(f"❌ Error al ejecutar la consulta: {e}")
        finally:
            cursor.close()
            conn.close()
