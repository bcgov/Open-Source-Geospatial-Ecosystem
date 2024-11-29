
from dotenv import load_dotenv
import os 
import requests
import json
import geojson
import logging 

load_dotenv()
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),  '../../../backend/.env')
load_dotenv(env_path)

api_key = os.getenv("NL_API")

# Base URL
base_url = "https://native-land.ca/api/index.php"

# Parameters for the query
params = {
    "maps": "languages,territories",  # Categories to query
    "name": "gitanyow-laxyip",  # Latitude and Longitude
    "key": api_key  # API key
}

# Make the GET request
response = requests.get(base_url, params=params)

# Check the response status
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    data=data[0]
else:
    logging.error(f"Error: {response.status_code}")
    logging.debug(response.text)
    
geojson_data = {
    "type": "FeatureCollection",
    "features": [data]
}