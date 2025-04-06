from app import create_app

# ⚠️ Asegúrate de que esta variable se llame EXACTAMENTE 'app' para Gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)  # Debug=False en producción
