from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import jwt
import os
from models.freelancer_application_model import  apply_for_work  # Import the model functions
from utils.verify_token import verify_token


app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes

# Secret key for encoding the JWT
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  # Replace with a strong secret key


def apply_for_work_controller():
    # Verify the token and extract the user_id
    user_id = verify_token()
    # Get data from the request
    data = request.get_json()
    cover_letter = data.get('cover_letter')
    time_to_complete = data.get('time_to_complete')

    if not cover_letter or not time_to_complete:
        return jsonify({"error": "Missing required fields"}), 400

    # Call the model function to apply for work
    result, status_code = apply_for_work(user_id, cover_letter, time_to_complete)

    return jsonify(result), status_code


if __name__ == '__main__':
    app.run(debug=True)
