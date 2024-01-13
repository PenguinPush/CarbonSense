from flask import Flask, url_for, render_template, redirect

app = Flask(__name__)

shopping_list = []

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/transit')
def transit():
    return render_template('transit.html')


@app.route('/shopping')
def shopping():
    if request.method == 'POST':
        item = request.form.get('item')
        quantity = int(request.form.get('quantity'))

        # Append the item and quantity to the shopping list
        shopping_list.append({'item': item, 'quantity': quantity})

    return render_template('shopping.html', shopping_list=shopping_list)

if __name__ == "__main__":
    app.run(debug=True)
