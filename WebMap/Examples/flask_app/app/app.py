from flask import Flask, render_template
from blueprints.overview_map import blueprint as over_map
from blueprints.intersect import blueprint as intersect
from flask_caching import Cache

#create app
app = Flask(__name__)

#set up caching
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# Set the secret key 
app.secret_key = 'FOSS4G_Test'
app.register_blueprint(over_map)
app.register_blueprint(intersect)

@app.route("/")
def app_root():
    #adjust message to return different request msg
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True)   #debug=True

