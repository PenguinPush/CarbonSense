from flask import Flask, url_for, render_template, redirect
from views import views

app = Flask(__name__)
app.register_blueprint(views)

if __name__ == "__main__":
    app.run(debug=True)