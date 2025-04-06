from app import create_app
from app.config.connection import Database

app = create_app()

if __name__ == "__main__":
    # Verificar la conexión a la base de datos
    try:
        db = Database()
        connection = db.get_connection()

        if connection:  # ✅ Correcto para pyodbc
            print("✅ Conexión exitosa a la base de datos")
        else:
            print("❌ Error al conectar a la base de datos")

        connection.close()
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")

    app.run(debug=True, host="0.0.0.0", port=5000)
