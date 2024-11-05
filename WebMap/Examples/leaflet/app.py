from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

WFS_URL = "https://openmaps.gov.bc.ca/geo/pub/ows?"  # WFS endpoint

@app.route('/wfs/<path:endpoint>', methods=['GET', 'POST', 'OPTIONS'])
def proxy_request(endpoint):
    # Construct the URL for the WFS request
    url = f"{WFS_URL}{endpoint}"

    # Forward the parameters from the request
    params = request.args.to_dict()

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
    app.run(host='0.0.0.0', port=5000)