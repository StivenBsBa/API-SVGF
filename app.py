from app import create_app

# ¡Cambia el nombre a "application"!
application = create_app()


# Esta función es necesaria para algunos servidores WSGI
def app(environ, start_response):
    return application(environ, start_response)


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000)
