from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import googlemaps
from config import GOOGLE_MAPS_API_KEY

app = Flask(__name__)
Bootstrap(app)
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/directions', methods=['POST'])
def directions():
    origin = request.form['origin']
    destination = request.form['destination']

    directions_result = gmaps.directions(origin, destination, mode="transit")

    return render_template('directions.html', directions=directions_result)

if __name__ == '__main__':
    app.run(debug=True)


