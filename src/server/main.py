# Import the Flask module and a few other helpers.
from flask import Flask, jsonify, request
from errors import misconfigured_clock
import time

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
    # To reduce latency inaccuracies, we're going to measure the timestamp as soon as the request is received.
    current_timestamp = time.time()
    
    # Read the body of the request.
    body = request.get_json()

    # Retrieve the timestamp from the request and subtract it from the current timestamp.
    past_timestamp = body.get("timestamp")
    drift_timestamp = current_timestamp - past_timestamp

    # Verify that the timestamp makes sense.
    if (drift_timestamp < 0):

        # If we've branched here, then the timestamp is in the future. Our or the client's clock is wrong.
        return misconfigured_clock()

    # Otherwise, the timestamp is valid. Our drift timestamp is thus our latency.
    return jsonify({

        "latency": drift_timestamp,

    }), 200