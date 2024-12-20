
from dotenv import load_dotenv
import os 
import requests
import json
import geojson
import logging 
def get_gitanyow():
    load_dotenv()
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),  '../../../backend/.env')
    load_dotenv(env_path)

    api_key = os.getenv("NL_API")

    # Base URL
    base_url = "https://native-land.ca/api/index.php"

    # Parameters for the query
    params = {
        "maps": "territories",  # Categories to query
        "name": "gitanyow-laxyip",  # Latitude and Longitude
        "key": api_key  # API key
    }

    # Make the GET request
    response = requests.get(base_url, params=params)

    # Check the response status
    if response.status_code == 200:
        # Parse the JSON response
        # data = response.json()
        # data=data[0]
        response_url = response.url
        # print("Response URL:", response_url)
    else:
        logging.error(f"Error: {response.status_code}")
        logging.debug(response.text)
    
    return response_url 

git_url=get_gitanyow()
print(git_url)