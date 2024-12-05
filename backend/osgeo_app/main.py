from . import app
import os

if __name__ == '__main__':
    app = app.create_app()
    app.run(debug=False)
else:
    gunicorn_app = app.create_app()
    gunicorn_app.config['DEBUG'] =  False
