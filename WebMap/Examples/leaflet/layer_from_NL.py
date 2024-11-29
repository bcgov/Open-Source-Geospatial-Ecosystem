
from dotenv import load_dotenv
import os 
import requests

load_dotenv()

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),  '../../../backend/.env')
load_dotenv(env_path)

api_key = os.getenv("NL_API")
# print(f"Your API key is: {api_key}")

url = "https://native-land.ca/api/index.php"
params = {
    "maps": "territories",
    "name": "gitanyow",
    "key": api_key,  # Replace 'key' with the correct parameter name if needed
}

response = requests.get(url, params=params)

print("Request URL:", response.url)
print("Response content:", response.text)