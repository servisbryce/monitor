# Import the Flask module and a few other helpers.
from flask import Flask, jsonify, request

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

# Define a route for a client to measure latency between the client and server. This route shall not be protected as it doesn't reveal any sensitive information.
@app.route("/latency", methods=["POST"])
def latency():

    body = request.get_json()
    # Ensure that the request actually has a body.
    if body:
        print("hi")

    else:
        # Alert the client that the request didn't succeed and the request is malformed.
        return jsonify({

            "status": "failure",
            "message": "malformed request"

        }), 400