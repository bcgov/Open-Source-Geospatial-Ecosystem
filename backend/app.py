from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
import requests

# Create app
app = Flask(__name__,
            static_folder='../frontend/static',  
            template_folder='../frontend/templates')  

# Enable CORS for all routes
CORS(app)

# Set up caching
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# Set the secret key
app.secret_key = 'FOSS4G_Test'

# WFS endpoint
WFS_URL = """https://openmaps.gov.bc.ca/geo/pub/ows?"""

# Register blueprints
from blueprints.overview_map import blueprint as over_map
from blueprints.intersect import blueprint as intersect
app.register_blueprint(over_map)
app.register_blueprint(intersect)

@app.route("/")
def app_root():
    # Render the main page
    return render_template('index.html')

@app.route('/plugins/<path:filename>')
def serve_node_modules(filename):
    return send_from_directory('../frontend/plugins/', filename)

# WFS proxy route
@app.route('/wfs<path:endpoint>', methods=['GET', 'POST', 'OPTIONS'])
def proxy_request(endpoint):
    # Construct the URL for the WFS request
    url = f"{WFS_URL}{endpoint}"

    # Forward the parameters from the request
    params = request.args.to_dict()

    print("Requesting URL:", url)
    print("Params:", params)
    
    # Handle HTTP methods appropriately
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == 'GET':
        wfs_response = requests.get(url, params=params)
    elif request.method == 'POST':
        wfs_response = requests.post(url, data=request.data)

    # Pass the content of the WFS response back to the client
    response = Response(wfs_response.content, status=wfs_response.status_code)
    response.headers['Content-Type'] = wfs_response.headers.get('Content-Type', 'application/json')

    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    return response

def _build_cors_preflight_response():
    """Handles the CORS preflight (OPTIONS) request."""
    response = Response(status=204)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
