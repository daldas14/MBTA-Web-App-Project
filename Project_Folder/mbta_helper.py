import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

if MAPBOX_TOKEN is None:
    raise RuntimeError("MAPBOX_TOKEN is not set. Check your .env file.")
if MBTA_API_KEY is None:
    raise RuntimeError("MBTA_API_KEY is not set. Check your .env file.")

MAPBOX_BASE_URL = "https://api.mapbox.com/search/searchbox/v1/forward"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"


def get_json(url):
    try:
        with urllib.request.urlopen(url) as response:
            response_text = response.read().decode("utf-8")
            response_data = json.loads(response_text)
            return response_data
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise Exception("Invalid API key. Please check your .env file.")
        elif e.code == 429:
            raise Exception("Too many requests. Please wait a moment and try again.")
        else:
            raise Exception(f"API request failed with error code {e.code}")
    except urllib.error.URLError:
        raise Exception("Cannot connect to the internet. Please check your connection.")
    except json.JSONDecodeError:
        raise Exception("Received invalid data from the API.")


def get_lat_lng(place_name):
    query = urllib.parse.quote(place_name)
    url = f"{MAPBOX_BASE_URL}?q={query}&access_token={MAPBOX_TOKEN}"
    response_data = get_json(url)
    
    if not response_data.get("features") or len(response_data["features"]) == 0:
        raise Exception(f"Location '{place_name}' not found. Try a different search term.")
    
    coordinates = response_data["features"][0]["geometry"]["coordinates"]
    longitude = str(coordinates[0])
    latitude = str(coordinates[1])
    return latitude, longitude


def get_nearest_station(latitude, longitude):
    params = {
        "api_key": MBTA_API_KEY,
        "sort": "distance",
        "filter[latitude]": latitude,
        "filter[longitude]": longitude
    }
    query_string = urllib.parse.urlencode(params)
    url = f"{MBTA_BASE_URL}?{query_string}"
    response_data = get_json(url)
    
    if not response_data.get("data") or len(response_data["data"]) == 0:
        raise Exception("No MBTA stations found near this location.")