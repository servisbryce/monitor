from flask import jsonify

# Define a function to alert the client that the request didn't succeed because the timestamp drift is negative.
def misconfigured_clock():

    # Alert the client that the request didn't succeed and the request is therefore invalid.
    return jsonify({

        "message": "The timestamp indicates that you are from the future. Please verify your clock synchronization.",

    }), 400

# Define a function to alert the client that the request didn't succeed because they aren't authorized.
def unauthorized_request():
    
    # Alert the client that the request didn't succeed and the request is therefore invalid.
    return jsonify({

        "message": "You're not permitted to access this endpoint.",

    }), 401