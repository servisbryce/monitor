from flask import jsonify

# Define a function to alert the client that the request didn't succeed because the timestamp drift is negative.
def misconfigured_clock():

    # Alert the client that the request didn't succeed and the request is therefore invalid.
    return jsonify({

        "message": "The timestamp is in the future. Please verify your clock synchronization.",

    }), 400