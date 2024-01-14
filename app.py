from flask import Flask, url_for, render_template, redirect, request, session
import requests
from openai import OpenAI
import json
import secrets
import random
client = OpenAI(api_key='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')
google_maps_api_key = 'AIzaSyCMPdLpbgwvxDXT02Fwk8mqHfNPqop6rxk'

# carbon_counter = client.beta.assistants.create(
#     instructions="Treat an input of a JSON shopping list with parameters like item, quantity, and weight and return an estimate of carbon emissions in metric format for each item purchased in a JSON format with the parameters item, quantity, and carbon emissions per item. Use your knowledge to calculate it.",
#     name="Carl the Carbon Counter",
#     model="gpt-4",
# )

carbon_counter = client.beta.assistants.retrieve(assistant_id='asst_qiKqmLTo9D8iwgCdOYezPno4')
thread = client.beta.threads.create()

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

history = [
    {'item': 'Water Bottles', 'quantity': 24, 'individual_carbon_emissions_kg': 0.082,
     'total_carbon_emissions_kg': 1.968,
     'trivia': 'The carbon emissions from producing 24 water bottles could fill nearly 237 basketballs!'},
    {'item': 'Industrial Revolution', 'quantity': 1, 'individual_carbon_emissions_kg': 200000000000,
     'total_carbon_emissions_kg': 200000000000,
     'trivia': 'The carbon emissions during the Industrial Revolution paved the way for the modern anthropogenic climate change.'},
    {'item': 'Taylor Swift Concert', 'quantity': 1, 'individual_carbon_emissions_kg': 27500,
     'total_carbon_emissions_kg': 27500,
     'trivia': 'The carbon emissions from a Taylor Swift Concert equates to flying a plane around the world over 5 times!'},
    {'item': 'Charging Smartphone', 'quantity': 1, 'individual_carbon_emissions_kg': 0.005,
     'total_carbon_emissions_kg': 0.005,
     'trivia': 'Did you know? The carbon emissions from charging a smartphone are equivalent to driving a regular car for about 15 meters.'},
    {'item': 'Pizza Slice', 'quantity': 5, 'individual_carbon_emissions_kg': 0.36, 'total_carbon_emissions_kg': 1.8,
     'trivia': 'Fun fact, the total carbon emissions of 5 pizza slices is roughly the same as charging 363 smartphones!'}
]

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
            #route = data['routes'][0]['overview_polyline']['points']
            return distance
        else:
            return None

def estimate_carbon_emissions(distance):
        distance_num = ''.join(char for char in distance if char.isdigit())
        spent_carbon = int(distance_num) * 0.206
        return round(spent_carbon, 2)

@app.route('/calculate')
def calculate():
     global distance
     global route
     global transit_emissions
     distance = calculate_distance_and_route(google_maps_api_key, origin, destination)
     transit_emissions = estimate_carbon_emissions(distance)
     return(redirect('/transit'))

@app.route('/transit', methods=['GET', 'POST'])
def transit():

    if request.method == 'POST':
         global origin
         global destination
         origin = request.form.get('origin')
         destination = request.form.get('destination')
         return redirect('/calculate')

    try:
        info = f"Distance on road: {distance}\n {transit_emissions} kg of CO2!" 
    except:
        info = ""
    return render_template('transit.html', info=info)

        #origin_location = input("Enter the origin location: ")
        #destination_location = input("Enter the destination location: ")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        global item
        item = request.form.get('item')
        return redirect('/get_json')

    return render_template('index.html', history=history)


@app.route('/get_json')
def get_json():
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=item
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

            shopping_list_parsed = str(messages.data[0].content[0].text.value)
            shopping_list_parsed = json.loads(shopping_list_parsed)

            session['shopping_list_parsed'] = shopping_list_parsed

            history.insert(0, shopping_list_parsed)

            print(shopping_list_parsed)

            return redirect('/')

percent_proximity = 0.8
max_range = 10

def generate_game():

    percent_proximity = 0.8

    list_of_objects = ["plastic water bottle(s)", "plastic bag(s)", "world domination(s)"]
    list_of_emissions = [3, 4, 5]  # in kg 

    object_one_index = random.randint(0, len(list_of_objects)-1)
    object_two_index = random.randint(0, len(list_of_objects)-1)

    amt_of_object_one = random.randint(1, max_range)
    approx_total_object_two_emissions = None
    # do the fancy chat gpt thing and get both object 1 and 2 emissions (should be per unit)
    object_one_emissions = list_of_emissions[object_one_index]
    object_two_emissions = list_of_emissions[object_two_index]

    if object_two_emissions > object_one_emissions:
        object_one_emissions, object_two_emissions = object_two_emissions, object_one_emissions
        object_one_index, object_two_index = object_two_index, object_one_index

    total_object_one_emissions = object_one_emissions * amt_of_object_one

    approx_total_object_two_emissions = object_one_emissions + (random.uniform(-1, 1) * percent_proximity * object_one_emissions)

    amt_of_object_two = approx_total_object_two_emissions // object_two_emissions
    amt_of_object_two = int(amt_of_object_two)
    if amt_of_object_two == 0:
         amt_of_object_two == 1
    total_object_two_emissions = amt_of_object_two * object_two_emissions

    if total_object_one_emissions > total_object_two_emissions:
        answer = "one"
    else:
         answer = "two"
    
    return [list_of_objects[object_one_index], amt_of_object_one, list_of_objects[object_two_index], amt_of_object_two, total_object_one_emissions, total_object_two_emissions, answer]

@app.route('/game', methods=['GET', 'POST'])
def game():
    result = None
    obj_one, num_obj_one, obj_two, num_obj_two, total_one, total_two, answer = generate_game()
    if request.method == 'POST':
        answerOne = request.form.get("one")
        answerTwo = request.form.get("two")
        print(answerOne)
        print(answerTwo)
        if answerOne is not None and answer=="one":
             result = "Correct"
        if answerTwo is not None and answer=="two":
             result = "Correct"
        if answerOne is not None and answer=="two":
             result = "Wrong"
        else:
             result = "Wrong"
    return render_template('game.html', object_one=obj_one, amt_of_one=num_obj_one, object_two=obj_two, amt_of_two=num_obj_two, total_one=total_one, total_two=total_two, result=result)

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=True)
