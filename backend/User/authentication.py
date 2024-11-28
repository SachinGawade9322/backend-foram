from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import re
import jwt  
import os
import datetime
from connection import get_db_connection  # Import the get_db_connection from connection.py


app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes

# Secret key for encoding the JWT
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") # Replace with a strong secret key

# Validation function for password strength (optional)
def is_password_strong(password):
    # Ensure password has at least 8 characters, one uppercase, one lowercase, one number, and one special character
    if (len(password) >= 8 and re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*()_+=\-]", password)):
        return True
    return False



def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# Registration endpoint
def register():
    # Get data from request
    data = request.get_json()

    # Extract fields
    firstname = data.get('firstName')
    lastname = data.get('lastName')
    account_type = data.get('accountType')
    email = data.get('email')
    mobile_no = data.get('mobileNo')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    # Validate fields
    if not firstname or not lastname or not account_type or not email or not mobile_no or not password or not confirm_password:
        return jsonify({"error": "All fields are required"}), 400

    if not is_password_strong(password):
        return jsonify({"error": "Password is too weak"}), 400

    if password != confirm_password:
        return jsonify({"error": "Password and confirm password should be the same!"}), 400

    # Hash the password before storing it (for security)
    hashed_password = generate_password_hash(password)

    # Insert user data into the PostgreSQL database
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if email already exists in the database
        cur.execute("SELECT * FROM Users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400

        # Insert new user
        cur.execute("""
            INSERT INTO Users (firstname, lastname, account_type, email, mobile_no, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (firstname, lastname, account_type, email, mobile_no, hashed_password))

        # Commit the transaction
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Login endpoint
def login():
    # Get data from request
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = None
    cur = None
    
    # Validate input
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch user data by email
        cur.execute("SELECT * FROM Users WHERE email = %s", (email,))
        user = cur.fetchone()

        # Close the database connection
        # cur.close()
        # conn.close()

        # Check if user exists and password is correct
        if user and check_password_hash(user[6], password):  # Assuming password hash is stored in the 6th column
            # Generate JWT token
            token = jwt.encode({
                'user_id': user[0],  # assuming user_id is the first column in the users table
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            
            # Prepare the response
            user_details = {
                "id": user[0],
                "firstname": user[1],
                "lastname": user[2],
                "account_type" : user[3],
                "email" : user[4],
                "mobile_no": user[5],
                "profile_photo" : user[7],
                "country": user[8],
                "working_domain": user[9],
                "technical_skills": user[10],
                "work_experience": user[11],
                "educational_details": user[12],
                "hourly_rate": user[13],
                "social_media_links": user[14],
                "connects": user[15]
            }
    
    
            # Create response object and set the JWT as a cookie
            response = make_response(jsonify({"message": "Login successful",  "user": user_details}), 200)
            response.set_cookie('token', token, httponly=True, secure=True, max_age=datetime.timedelta(hours=1))  # Set JWT token as cookie
            
            return response
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the cursor and connection safely
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()



# Logout endpoint
def logout():
    
    token = ""

    # Extracting the token from the Authorization header or cookies
    auth_header = request.headers.get('Authorization')
    access_token = request.cookies.get('token')

    print(access_token)

    if not auth_header and not access_token:
        return jsonify({"error": "Authorization header or token missing"}), 401

    if auth_header:
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    elif access_token:
        token = access_token

    # Decode the JWT token
    decoded_token = decode_jwt_token(token)
    if not decoded_token:
        return jsonify({"error": "Invalid or expired token"}), 401

    user_id = decoded_token.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400

    # Create response to clear the token cookie
    res = make_response(jsonify({"message": "Logout successful"}), 200)
    res.set_cookie('token', '', httponly=True, secure=True, expires=0)

    return res



if __name__ == '__main__':
    app.run(debug=True)
