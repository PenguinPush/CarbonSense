from flask import Flask, url_for, render_template, redirect, request, jsonify

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

@app.route('/get_json')
def get_json():
    # Convert the shopping list to JSON and return it
    return jsonify(shopping_list)

if __name__ == "__main__":
    app.run(debug=True)
