from connection import get_db_connection
from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import re
import jwt  
import os
import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes

# Secret key for encoding the JWT
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") # Replace with a strong secret key


# Function for get token of login user
def verify_token():
    token= ""

    auth_header = request.headers.get('Authorization')
    accessToken  = request.cookies.get('token');

    if not auth_header and not accessToken:
        return jsonify({"error": "Authorization header or token missing"}), 401

    if auth_header:
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    elif accessToken:
        token = accessToken
    decoded_token = decode_jwt_token(token)
    if not decoded_token:
        return jsonify({"error": "Invalid or expired token"}), 401

    user_id = decoded_token.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400
            
    return user_id

# Decode JWT function
def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def apply_for_work():
    # Verify the token and extract the user_id
    user_id = verify_token()
    if isinstance(user_id, tuple):  # If `verify_token` returns a tuple, it's an error
        return user_id

    # Get data from the request
    data = request.get_json()
    cover_letter = data.get('cover_letter')
    time_to_complete = data.get('time_to_complete')

    if not cover_letter or not time_to_complete:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cursor = conn.cursor()

        # Decrease the 'connects' count by 1
        cursor.execute("""
            UPDATE users
            SET connects = connects - 5
            WHERE id = %s AND connects > 0
            RETURNING connects;
        """, (user_id,))

        result = cursor.fetchone()
        if not result:
            conn.rollback()
            return jsonify({"error": "Insufficient connects or invalid user"}), 400

        remaining_connects = result[0]

        # Insert the application details into freelancerApplications
        cursor.execute("""
            INSERT INTO freelancerApplications (user_id, cover_letter, time_to_complete)
            VALUES (%s, %s, %s)
            RETURNING application_id;
        """, (user_id, cover_letter, time_to_complete))

        application_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "message": "Application submitted successfully",
            "application_id": application_id,
            "remaining_connects": remaining_connects
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Failed to submit application: {e}"}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
