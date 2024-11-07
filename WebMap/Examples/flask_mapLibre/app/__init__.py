from flask import Flask, render_template


def create_app():
    app = Flask(__name__)
    return app


app = create_app()


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000, threaded=True)