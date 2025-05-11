# Import the database module.
from database import Record

# Import the Flask server.
from flask import Flask, request, jsonify, abort

# Import rate limiters.
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Import other modules.
import time

# Define our application.
monitor = Flask(__name__)

# Define our ratelimits.
limiter = Limiter(

    app=monitor,
    key_func=get_remote_address,
    default_limits=["60 per hour"]

)

# Define our application secrets.
application_secrets = [

    "development_key_1"

]

# Authentication middleware.
def authenticate(body):
    
    # Attempt to retrieve the token and compare it to the known list of valid tokens.
    try:

        if body["token"] not in application_secrets:
            raise ValueError("Invalid token.")
        
    # If the token is present but invalid, we'll declare it.
    except ValueError as error_message:
        abort(403, error_message)

    # Otherwise, there isn't a token present in the body, so we'll throw the relevant error code and abort.
    except:
        abort(401, "There is no token present.")

# An endpoint to report latency to the server.
@monitor.route("/api/v1/report_latency", methods=["POST"])
def report_latency():

    # Retrieve the request body which should be a JSON object.
    body = request.get_json()
    
    # Catch any authorization errors right away before they make it into the rest of the program.
    authenticate(body)

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

        "message": "Success",
        "network_latency": network_latency

    }, 200)

# An endpoint to report network interfaces.
@monitor.route("/api/v1/report_network_interface", methods=["POST"])
def report_network_interface():

    # Retrieve request body which should be a JSON object.
    body = request.get_json()

    # Authenticate the request to ensure that it's valid.
    authenticate(body)

    # Store our values to retrieve out of the request.
    network_interface_schema = {

        "name": None,
        "ipv6": None,
        "ipv4": None,
        "mac": None 

    }

    # Attempt to retrieve all of our data from the request.
    try:

        # Populate our table.
        network_interface_schema["name"] = body["name"]
        network_interface_schema["ipv6"] = body["ipv6"]
        network_interface_schema["ipv4"] = body["ipv4"]
        network_interface_schema["mac"] = body["mac"]

    except:

        # Alert the request that their message isn't valid.
        abort(400, "Corrupted or malformed request.")

    # Check that there aren't any null values where they aren't warranted. Addresses receive an exception because an interface may not always have an address assigned to it at a given time.
    if (network_interface_schema["name"] is None or network_interface_schema["mac"] is None or (network_interface_schema["ipv4"] is None and network_interface_schema["ipv6"] is None)):
        abort(400, "Corrupted or malformed request.")

    # We'll also want to make sure that all of our values are strings, if they aren't empty address fields.
    if (not isinstance(body["name"], str) or (not isinstance(body["mac"], str)) or ((not isinstance(body["ipv4"], str)) and (not isinstance(body["ipv6"], str)))):
        abort(400, "Corrupted or malformed request.")

    # Update our database record.
    client_record = Record(body["token"])
    client_record.set_network_interfaces(network_interface_schema)

    # Reaffirm success to client.
    return jsonify({

        "message": "Success"

    }, 200)