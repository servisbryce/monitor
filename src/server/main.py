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

        # Check if there is a record of the client in the database already.
        try:
            # Check if there is a record of the client in the database already.
            client_record = db[client_token]

            # Deserialize the client record.
            client_record = json.loads(client_record)

            # Update the client record with the new data.
            client_record["updated_at"] = current_timestamp
            client_record["events"].append({

                "requested_at": current_timestamp,
                "latency": drift_timestamp,
                "route": "/latency"

            })

            # Serialize the updated client record.
            client_record = json.dumps(client_record)

            # Update the client record in the database.
            db[client_token] = client_record

        except KeyError:
            # If not, then create a new record for the client.
            client_record = {

                "created_at": current_timestamp,
                "updated_at": current_timestamp,
                "events": [

                    {

                        "requested_at": current_timestamp,
                        "latency": drift_timestamp,
                        "route": "/latency"

                    }

                ],

                "token": client_token

            }

            # Serialize the client record.
            client_record = json.dumps(client_record)

            # Add the client record to the database.
            db[client_token] = client_record

    # Just return the data snippet from earlier to the client.
    return jsonify({

        "requested_at": current_timestamp,
        "latency": drift_timestamp,
        "route": "/latency"

    }), 200