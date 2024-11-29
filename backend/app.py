from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
import requests
from dotenv import load_dotenv
import os 


load_dotenv()

api_key = os.getenv("NL_API")

# Create app
app = Flask(__name__,
            static_folder='./templates/static',  
            template_folder='./templates/templates')  

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

@app.route('/templates/plugins/<path:filename>')
def serve_node_modules(filename):
    return send_from_directory('./templates/plugins', filename)

# WFS proxy route
@app.route('/wfs<path:endpoint>', methods=['GET', 'POST', 'OPTIONS'])
def proxy_request(endpoint):
    # Construct the base URL
    url = f"{WFS_URL}{endpoint}"

    # Collect parameters and headers
    params = request.args.to_dict()
    headers = dict(request.headers)
    headers.pop('Host', None)  # Avoid host mismatches

    # Handle preflight CORS (OPTIONS request)
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    # Forward GET or POST requests to the WFS server
    try:
        if request.method == 'GET':
            wfs_response = requests.get(url, params=params, headers=headers)
        elif request.method == 'POST':
            wfs_response = requests.post(url, data=request.data, headers=headers)

        # Build the Flask response
        response = Response(wfs_response.content, status=wfs_response.status_code)
        response.headers['Content-Type'] = wfs_response.headers.get('Content-Type')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        # Debugging
        print("Request URL:", wfs_response.url)
        print("Response Status:", wfs_response.status_code)
        print("Response Content-Type:", wfs_response.headers.get('Content-Type'))
        return response

    except requests.RequestException as e:
        print("Request Error:", e)
        return Response("Error connecting to WFS server", status=500)


def _build_cors_preflight_response():
    """Handles the CORS preflight (OPTIONS) request."""
    response = Response(status=204)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
