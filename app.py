import openai
from flask import Flask, url_for, render_template, redirect, request, jsonify
from openai import OpenAI

client = OpenAI(api_key='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')

# carbon_counter = client.beta.assistants.create(
#     instructions="Treat an input of a JSON shopping list with parameters like item, quantity, and weight and return an estimate of carbon emissions in metric format for each item purchased in a JSON format with the parameters item, quantity, and carbon emissions per item. Use your knowledge to calculate it.",
#     name="Carl the Carbon Counter",
#     model="gpt-4",
# )

carbon_counter = client.beta.assistants.retrieve(assistant_id='asst_5f1AdNw2sy4HOQwCufkdZqtH')

print(carbon_counter)

app = Flask(__name__)

shopping_list = []

@app.route("/")
def home():
    return redirect(url_for('shopping'))


@app.route('/transit')
def transit():
    return render_template('transit.html')



@app.route('/shopping', methods=['GET', 'POST'])
def shopping():
    if request.method == 'POST':
        item = request.form.get('item')
        quantity = int(request.form.get('quantity'))

        # Append the item, quantity, and weight to the shopping list
        shopping_list.append({
            'item': item,
            'quantity': quantity,
        })

    return render_template('shopping.html', shopping_list=shopping_list)


@app.route('/remove_item', methods=['POST'])
def remove_item():
    item_to_remove = request.form.get('item_to_remove')

    # Remove the item from the shopping list
    shopping_list[:] = [item for item in shopping_list if item['item'] != item_to_remove]

    return redirect(url_for('shopping'))


@app.route('/get_json')
def get_json():
    # Convert the shopping list to JSON and return it
    return jsonify(shopping_list)

if __name__ == "__main__":
    app.run(debug=True)

import requests

import requests


def calculate_distance_and_route(api_key, origin, destination):
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        'origin': origin,
        'destination': destination,
        'key': api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        # Extract distance and route information
        distance = data['routes'][0]['legs'][0]['distance']['text']
        route = data['routes'][0]['overview_polyline']['points']
        return distance, route
    else:
        return None, None


def suggest_alternate_route(api_key, origin, destination):
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        'origin': origin,
        'destination': destination,
        'mode': 'transit',
        'key': api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        # Extract alternate route information
        transit_route = data['routes'][0]['overview_polyline']['points']
        return transit_route
    else:
        return None


from flask import Flask, render_template, request

app = Flask(__name__)

# Paste your functions here

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        origin_location = request.form['origin_location']
        destination_location = request.form['destination_location']

        # Call your functions here
        distance, route = calculate_distance_and_route(google_maps_api_key, origin_location, destination_location)

        if distance and route:
            # Estimate carbon emissions (replace with your chosen carbon estimation logic)
            carbon_emission_estimate = estimate_carbon_emissions(distance, transportation_mode='driving')

            # Suggest alternate route with transit
            transit_route = suggest_alternate_route(google_maps_api_key, origin_location, destination_location)

            return render_template('result.html', distance=distance, route=route,
                                   carbon_emission_estimate=carbon_emission_estimate, transit_route=transit_route)
        else:
            return render_template('error.html')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

