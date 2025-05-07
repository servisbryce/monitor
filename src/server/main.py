# Import the Flask module and a few other helpers.
from flask import Flask, jsonify, request
from errors import misconfigured_clock, unauthorized_request
import time, dbm, json

# Define the Flask application.
app = Flask(__name__)

# Define metadata about the application in a table.
application_metadata = {

    "application": "monitor",
    "version": "0.1",

}

# Define our application keys. These values are used for testing purposes. Don't use these in production.
client_tokens = [

    "development_key_1"

]

# Define the default route
@app.route("/")
def root():
    return jsonify(application_metadata)

# Define a route for a client to measure latency between the client and server.
@app.route("/latency", methods=["POST"])
def latency():
    # To reduce latency inaccuracies, we're going to measure the timestamp as soon as the request is received.
    current_timestamp = time.time()
    
    # Read the body of the request.
    body = request.get_json()

    # Authenticate the request.
    client_token = body.get("token")
    if client_token not in client_tokens:

        # If we've branched here, then the token is invalid. The client isn't permitted to make this request!
        return unauthorized_request()

    # Retrieve the timestamp from the request and subtract it from the current timestamp.
    past_timestamp = body.get("timestamp")
    drift_timestamp = current_timestamp - past_timestamp

    # Verify that the timestamp makes sense.
    if (drift_timestamp < 0):

        # If we've branched here, then the timestamp is in the future. Our or the client's clock is wrong.
        return misconfigured_clock()

    with dbm.open("monitor.db", "c") as db:

        # Construct our object for the key-value store.
        latency_object = {

            "requested_at": current_timestamp,
            "latency": drift_timestamp,
            "token": client_token,

        }

        # Store the latency object in the key-value store.
        db[str(client_token) + "-latency"] = json.dumps(latency_object)

    # Otherwise, the timestamp is valid. Our drift timestamp is thus our latency.
    return jsonify({

        "latency": drift_timestamp,

    }), 200