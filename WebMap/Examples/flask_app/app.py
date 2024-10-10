from flask import Flask 
# from blueprints.map import blueprint as overview_map
from blueprints.intersect import blueprint as intersect
from flask_caching import Cache

#create app
app = Flask(__name__)

#set up caching
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# Set the secret key 
app.secret_key = 'FOSS4G_Test'
# app.register_blueprint(overview_map)
app.register_blueprint(intersect)

@app.route("/")
def app_root():
    #adjust message to return different request msg
    return "API is running",200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True)   #debug=True

