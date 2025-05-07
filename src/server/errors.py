from flask import jsonify

# Define a function to alert the client that the request didn't succeed and the request is malformed.
def malformed_request():
    
    # Alert the client that the request didn't succeed and the request is malformed.
    return jsonify({

        "status": "failure",
        "message": "malformed request"

    }), 400