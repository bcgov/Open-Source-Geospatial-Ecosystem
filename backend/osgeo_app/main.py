from . import app


if __name__ == '__main__':
    app = app.create_app()
    app.run(debug=True)
else:
    gunicorn_app = app.create_app()
    gunicorn_app.config['DEBUG'] = True
