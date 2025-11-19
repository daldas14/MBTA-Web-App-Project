from flask import Flask, render_template, request
import mbta_helper

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/nearest_mbta", methods=["POST"])
def nearest_mbta():
    try:
        place_name = request.form.get('place_name', '').strip()
        
        if not place_name:
            return render_template('error.html', 
                                 error_message="Please enter a location name.",
                                 error_type="empty_input")
        
        if len(place_name) < 2:
            return render_template('error.html',
                                 error_message="Location name is too short. Please enter at least 2 characters.",
                                 error_type="invalid_input")
        
        latitude, longitude = mbta_helper.get_lat_lng(place_name)
        station_name, wheelchair_accessible = mbta_helper.get_nearest_station(latitude, longitude)
        events = mbta_helper.get_nearby_events(latitude, longitude)
        
        return render_template('mbta_station.html', 
                             place_name=place_name, 
                             station_name=station_name, 
                             wheelchair_accessible=wheelchair_accessible,
                             events=events)
    
    except Exception as e:
        error_msg = str(e)
        
        if "not found" in error_msg.lower():
            error_type = "location_not_found"
        elif "no mbta stations" in error_msg.lower():
            error_type = "no_stations"
        elif "api key" in error_msg.lower():
            error_type = "api_error"
        elif "connect" in error_msg.lower():
            error_type = "connection_error"
        else:
            error_type = "general_error"
        
        return render_template('error.html', 
                             error_message=error_msg,
                             error_type=error_type)

if __name__ == "__main__":
    app.run(debug=True)