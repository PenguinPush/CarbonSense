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

history = []

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

            history.extend(shopping_list_parsed)

            print(shopping_list_parsed)

            return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)