# Import the Flask module.
from flask import Flask, jsonify

# Define the Flask application.
app = Flask(__name__)

# Define metadata about the application in a table.
application_metadata = {

    "application": "monitor",
    "version": "0.1",

}

# Define the default route
@app.route("/")
def root():
    return jsonify(application_metadata)

# Define a route