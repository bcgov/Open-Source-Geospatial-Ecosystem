from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
import requests
from dotenv import load_dotenv
import os 
import requests
import logging 

from blueprints.overview_map import blueprint as over_map
from blueprints.intersect import blueprint as intersect

# Create app
def create_app():
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
            logging.info("Request URL:", wfs_response.url)
            logging.info("Response Status:", wfs_response.status_code)
            logging.info("Response Content-Type:", wfs_response.headers.get('Content-Type'))
            return response

        except requests.RequestException as e:
            logging.debug("Request Error:", e)
            return Response("Error connecting to WFS server", status=500)


        except requests.RequestException as e:
            logging.debug("Request Error:", e)
            return Response("Error connecting to WFS server", status=500)


    #route to return Gitanyow area from Native Land API
    @app.route('/api/gitanyow-url', methods=['GET'])
    def gitanyow_url():
        try:
            response_url = get_gitanyow()
            return jsonify({"url": response_url})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app

#return link for Gitanyow Land Use Plan Boundary 
def get_gitanyow():
    load_dotenv()
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),  '../../../backend/.env')
    load_dotenv(env_path)

    api_key = os.getenv("NL_API")

    # Base URL
    base_url = "https://native-land.ca/api/index.php"

    # Parameters for the query
    params = {
        "maps": "territories",
        "name": "gitanyow-laxyip",
        "key": api_key
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        response_url = response.url
        logging.debug("Response URL:", response_url)
    else:
        logging.error(f"Error: {response.status_code}")
        logging.debug(response.text)
        
    return response_url

api_key = os.getenv("NL_API")

def _build_cors_preflight_response():
    """Handles the CORS preflight (OPTIONS) request."""
    response = Response(status=204)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, threaded=True)
