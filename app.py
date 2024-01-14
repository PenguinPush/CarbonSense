from flask import Flask, url_for, render_template, redirect, request, session
from openai import OpenAI
import json
import secrets
client = OpenAI(api_key='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')

# carbon_counter = client.beta.assistants.create(
#     instructions="Treat an input of a JSON shopping list with parameters like item, quantity, and weight and return an estimate of carbon emissions in metric format for each item purchased in a JSON format with the parameters item, quantity, and carbon emissions per item. Use your knowledge to calculate it.",
#     name="Carl the Carbon Counter",
#     model="gpt-4",
# )

carbon_counter = client.beta.assistants.retrieve(assistant_id='asst_qiKqmLTo9D8iwgCdOYezPno4')
thread = client.beta.threads.create()

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)


shopping_list = []
shopping_list_parsed = []


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/transit')
def transit():
    return render_template('transit.html')



@app.route('/shopping', methods=['GET', 'POST'])
def shopping():
    shopping_list_parsed = session.get('shopping_list_parsed', [])
    total_carbon_emissions = sum(item.get('total_carbon_emission_kg', 0) for item in shopping_list_parsed)

    if request.method == 'POST':
        # Process the shopping list as usual
        item = request.form.get('item')
        quantity = int(request.form.get('quantity'))

        shopping_list.append({
            'item': item,
            'quantity': quantity,
        })

    return render_template('shopping.html',
                           shopping_list=shopping_list,
                           shopping_list_parsed=shopping_list_parsed,
                           total_carbon_emissions=total_carbon_emissions
                           )


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

            shopping_list_parsed = str(messages.data[0].content[0].text.value)
            shopping_list_parsed = json.loads(shopping_list_parsed)

            session['shopping_list_parsed'] = shopping_list_parsed

            print(shopping_list_parsed)

            return redirect('/shopping')

if __name__ == "__main__":
    app.run(debug=True)