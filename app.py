from flask import Flask
app = Flask(__name__)

@app.route("/")
def wellcome():
    return "hello"

@app.route("/home")
def home():
    return "This is home page"

from controller import * 

# set PYTHONDONTWRITEBYTECODE=1
# $env:FLASK_APP = "app.py"
# $env:FLASK_ENV = "development"
# $env:FLASK_DEBUG = "1"
# flask run

