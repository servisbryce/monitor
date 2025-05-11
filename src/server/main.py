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
    if (network_interface_schema["name"] is None or network_interface_schema["mac"] is None):
        abort(400, "An essential value is set to null in the request.")

    # We'll also want to make sure that all of our values are strings, if they aren't empty address fields.
    if (not isinstance(body["name"], str) or (not isinstance(body["mac"], str))):
        abort(400, "An essential value isn't the correct type in the request.")

    # If either address value is set, we should also ensure that it's a string and not an alternative value.
    if (body["ipv6"] is not None and not isinstance(body["ipv6"], str)):
        abort(400, "The type for the IPv6 value isn't recognized in the request.")

    if (body["ipv4"] is not None and not isinstance(body["ipv4"], str)):
        abort(400, "The type for the IPv4 value isn't recognized in the request.")

    # Update our database record.
    client_record = Record(body["token"])
    client_record.set_network_interfaces(network_interface_schema)

    # Reaffirm success to client.
    return jsonify({

        "message": "Success"

    }, 200)

# An endpoint to report the CPU.
@monitor.route("/api/v1/report_cpu", methods=["POST"])
def report_cpu():
    
    # Retrieve body payload.
    body = request.get_json()

    # Authenticate the user.
    authenticate(body)

    # Define our schema.
    cpu_schema = {

        "threads": None,
        "cores": None,
        "model": None,
        "load": None

    }

    # Attempt to retrieve all of our data from the request.
    try:

        # Retrieve the data.
        cpu_schema["threads"] = body["threads"]
        cpu_schema["cores"] = body["cores"]
        cpu_schema["model"] = body["model"]
        cpu_schema["load"] = body["load"]

    except:

        # Abort if we're unable to find the necessary data in the request.
        abort(400, "Malformed or corrupted request.")

    # Ensure that our types are rigid and correct.
    if not isinstance(cpu_schema["threads"], int) or not isinstance(cpu_schema["cores"], int) or not isinstance(cpu_schema["model"], str) or not isinstance(cpu_schema["load"], float):
        abort(400, "Type-error in request.")

    # Update the database.
    client_record = Record(body["token"])
    client_record.set_cpu(cpu_schema)

    # Reaffirm success to client.
    return jsonify({

        "message": "Success"

    }, 200)

# An endpoint to report memory.
@monitor.route("/api/v1/report_memory", methods=["POST"])
def report_memory():

    # Request the body payload.
    body = request.get_json()

    # Authenticate our user.
    authenticate(body)

    # Define our schema.
    memory_schema = {

        "available": None,
        "used": None,
        "swap": None,

    }

    # Attempt to fetch our values from the request.
    try:

        # Fetch our necessary values.
        memory_schema["available"] = body["available"]
        memory_schema["used"] = body["used"]
        memory_schema["swap"] = body["swap"]

    except:

        # Abort if we struggle to find the required values.
        abort(400, "There was an error while trying to parse your request.")

    # Ensure that we validate our inputs.
    if (not isinstance(memory_schema["available"], int) or not isinstance(memory_schema["used"], int)):
        abort(400, "There was an invalid type detected while trying parsing your request.")

    if (not isinstance(memory_schema["swap"], dict) and not memory_schema["swap"] is None):
        abort(400, "There was an error while trying to verify the type of the swap object.")

    # If swap is populated, then we'll validate it as well.
    if (isinstance(memory_schema["swap"], dict)):

        # There is a chance that our values aren't present in the swap dict, so we'll need to use a try function here.
        try:

            # Ensure that our types are correct.
            if (not isinstance(memory_schema["swap"]["available"], int)):
                abort(400, "The swap segment of your request has an invalid type.")

            if (not isinstance(memory_schema["swap"]["used"], int)):
                abort(400, "The swap segment of your request has an invalid type.")

        except:

            # If these values couldn't be parsed, then we'll abort.
            abort(400, "The swap segment of your request couldn't be parsed.")

    # Update the database.
    client_record = Record(body["token"])
    client_record.set_memory(memory_schema)

    # Reaffirm success to client.
    return jsonify({

        "message": "Success"

    }, 200)