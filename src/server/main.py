# Import the database module.
from database import Record

# Import the Flask server.
from flask import Flask, request, jsonify, abort

# Import other modules.
import time

# Define our application.
monitor = Flask(__name__)

# Define our application secrets.
application_secrets = [

    "development_key_1"

]

# An endpoint to report latency to the server.
@monitor.route("/api/v1/report_latency", methods=["POST"])
def report_latency():

    # Retrieve the request body which should be a JSON object.
    body = request.get_json()
    
    # Catch any authorization errors right away before they make it into the rest of the program.
    try: 

        # Verify if the token in the body is valid.
        if body["token"] not in application_secrets:
            raise ValueError("Invalid token.")

    # If the token is present but invalid, then we'll declare it.
    except ValueError as error_message:

        # Declare the error to the client.
        abort(403, error_message)

    # Otherwise, there isn't a token present and we're going to report the proper error code.
    except:
        
        # If the token is not present, abort with a unauthorized error.
        abort(401, "There is no token present.")

    # If we've reached this part of the function, the used has authorized themselves. We'll try to grab the timestamp.
    requested_at = None
    try:

        # Try to retrieve the timestamp.
        requested_at = body["requested_at"]

    except:

        # We failed to retrieve the timestamp as it's not present.
        abort(400, "Requested at timestamp is missing from the request.")

    # Ensure that the timestamp is an integer, otherwise we'll run into type issues.
    if not isinstance(requested_at, int):

        # Report the error and abort.
        abort(400, "Requested at timestamp is not an integer.")

    # Calculate the latency.
    received_at = time.time()
    network_latency = received_at - requested_at

    # If we've received a message from the future, either someone has invented time travel or their clock is misconfigured.
    if (network_latency < 0):

        # Report the error to the client and abort.
        abort(400, "Either the server or client clock is misconfigured.")

    # If we've made it this far, we're able to go ahead and report the latency to the database.
    client_record = Record(body["token"])
    client_record.set_network_latency(network_latency)

    # Then, we'll respond to the client with the latency value we've recorded to complete the request.
    return jsonify({

        "network_latency": network_latency

    })

# An endpoint to report network interfaces.
@monitor.route("/api/v1/report_network_interfaces", method=["POST"])
def report_network_interfaces():

    # Retrieve request body which should be a JSON object.
    body = request.get_json()