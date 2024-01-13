import openai
from flask import Flask, url_for, render_template, redirect, request, jsonify
from openai import OpenAI
import requests
import json

client = OpenAI(api_key='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')

# carbon_counter = client.beta.assistants.create(
#     instructions="Treat an input of a JSON shopping list with parameters like item, quantity, and weight and return an estimate of carbon emissions in metric format for each item purchased in a JSON format with the parameters item, quantity, and carbon emissions per item. Use your knowledge to calculate it.",
#     name="Carl the Carbon Counter",
#     model="gpt-4",
# )

carbon_counter = client.beta.assistants.retrieve(assistant_id='asst_qiKqmLTo9D8iwgCdOYezPno4')
thread = client.beta.threads.create()

app = Flask(__name__)

shopping_list = []


@app.route("/")
def home():
    return redirect(url_for('shopping'))


@app.route('/transit')
def transit():
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


    def estimate_carbon_emissions(distance, transportation_mode):
        distance_num = ''.join(char for char in distance if char.isdigit())
        spent_carbon = int(distance_num) * 0.206
        return round(spent_carbon, 2)


    if __name__ == "__main__":
        google_maps_api_key = 'AIzaSyCMPdLpbgwvxDXT02Fwk8mqHfNPqop6rxk'

        # Get user input for origin and destination
        origin_location = input("Enter the origin location: ")
        destination_location = input("Enter the destination location: ")

        distance, route = calculate_distance_and_route(google_maps_api_key, origin_location, destination_location)
        if distance and route:
            print(f"Distance: {distance}")
            print(f"Route: {route}")

            # Estimate carbon emissions (replace with your chosen carbon estimation logic)
            carbon_emission_estimate = estimate_carbon_emissions(distance, transportation_mode='driving')
            print(f"Carbon Emission Estimate: {carbon_emission_estimate} kgCO2")

            # Suggest alternate route with transit
            transit_route = suggest_alternate_route(google_maps_api_key, origin_location, destination_location)
            if transit_route:
                print(f"Suggested Transit Route: {transit_route}")
        else:
            print("Error in route calculation.")
    return render_template('transit.html', distance=distance, decoded_route="wtf is a decoded route", carbon_emission_estimate=carbon_emission_estimate, transit_route=transit_route)


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
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=json.dumps(shopping_list)
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=carbon_counter.id
    )

    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run.status == "completed":
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )

            gpt_output = str(messages.data[0].content[0].text.value)
            shopping_list_parsed = (json.dumps(gpt_output))
            print(shopping_list_parsed)

            return redirect(url_for('shopping'))


if __name__ == "__main__":
    app.run(debug=True)


from flask import Flask, render_template, request
import polyline

app = Flask(__name__)

# ... (other functions)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        origin_location = request.form['origin_location']
        destination_location = request.form['destination_location']

        # Call your functions here
        distance, route = calculate_distance_and_route(google_maps_api_key, origin_location, destination_location)

        if distance and route:
            # Decode the polyline string
            decoded_route = polyline.decode(route)

            # Estimate carbon emissions (replace with your chosen carbon estimation logic)
            carbon_emission_estimate = estimate_carbon_emissions(distance, transportation_mode='driving')

            # Suggest alternate route with transit
            transit_route = suggest_alternate_route(google_maps_api_key, origin_location, destination_location)

            return render_template('result.html', distance=distance, decoded_route=decoded_route,
                                   carbon_emission_estimate=carbon_emission_estimate, transit_route=transit_route)
        else:
            return render_template('error.html')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

