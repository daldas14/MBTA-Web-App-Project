import os
import json
import pprint
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")

if MAPBOX_TOKEN is None:
    raise RuntimeError("MAPBOX_TOKEN is not set. Check your .env file.")
if MBTA_API_KEY is None:
    raise RuntimeError("MBTA_API_KEY is not set. Check your .env file.")

MAPBOX_BASE_URL = "https://api.mapbox.com/search/searchbox/v1/forward"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"


def get_json(url):
    with urllib.request.urlopen(url) as resp:
        response_text = resp.read().decode("utf-8")
        response_data = json.loads(response_text)
        return response_data


def get_lat_lng(place_name):
    query = urllib.parse.quote(place_name)
    url = f"{MAPBOX_BASE_URL}?q={query}&access_token={MAPBOX_TOKEN}"
    response_data = get_json(url)
    
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
    
    nearest_stop = response_data["data"][0]
    station_name = nearest_stop["attributes"]["name"]
    wheelchair_boarding = nearest_stop["attributes"]["wheelchair_boarding"]
    wheelchair_accessible = (wheelchair_boarding == 1)
    return station_name, wheelchair_accessible


def get_nearby_events(latitude, longitude, radius=5):
    if TICKETMASTER_API_KEY is None:
        return []
    
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={TICKETMASTER_API_KEY}&latlong={latitude},{longitude}&radius={radius}&unit=miles&size=3"
    
    try:
        response_data = get_json(url)
        
        if "_embedded" not in response_data or "events" not in response_data["_embedded"]:
            return []
        
        events = []
        for event in response_data["_embedded"]["events"]:
            event_name = event["name"]
            event_date = event["dates"]["start"]["localDate"]
            event_venue = event["_embedded"]["venues"][0]["name"]
            event_url = event.get("url", "#")
            
            events.append({
                "name": event_name,
                "date": event_date,
                "venue": event_venue,
                "url": event_url
            })
        
        return events
    except:
        return []


def find_stop_near(place_name):
    latitude, longitude = get_lat_lng(place_name)
    station_name, wheelchair_accessible = get_nearest_station(latitude, longitude)
    return station_name, wheelchair_accessible


def main():
    print("Testing get_lat_lng:")
    lat, lng = get_lat_lng("Boston Common")
    print(f"Latitude: {lat}, Longitude: {lng}")
    
    print("\nTesting get_nearest_station:")
    station, accessible = get_nearest_station(lat, lng)
    print(f"Station: {station}")
    print(f"Wheelchair Accessible: {accessible}")
    
    print("\nTesting find_stop_near:")
    station, accessible = find_stop_near("Fenway Park")
    print(f"Station: {station}")
    print(f"Wheelchair Accessible: {accessible}")
    
    print("\nTesting get_nearby_events:")
    events = get_nearby_events(lat, lng)
    print(f"Found {len(events)} events:")
    for event in events:
        print(f"  - {event['name']} on {event['date']} at {event['venue']}")


if __name__ == "__main__":
    main()