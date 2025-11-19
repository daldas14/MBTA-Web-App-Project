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
                                 error_message="Please enter a location name.")
        
        station_name, wheelchair_accessible = mbta_helper.find_stop_near(place_name)
        
        return render_template('mbta_station.html',
                             place_name=place_name,
                             station_name=station_name,
                             wheelchair_accessible=wheelchair_accessible)
    
    except Exception as e:
        error_message = f"Sorry, we couldn't find MBTA information for that location. {str(e)}"
        return render_template('error.html', error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True)