# Import the database module.
from database import Database

# Import the Flask server.
from flask import Flask, request, jsonify

@app.route("/", methods=["POST"])