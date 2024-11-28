import jwt
import os
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  # Replace with your actual secret key


# Decode JWT function
def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


# Function to get token of logged-in user
def verify_token():
    token = ""

    # Check if Authorization header or token in cookies is provided
    auth_header = request.headers.get('Authorization')
    accessToken = request.cookies.get('token')

    if not auth_header and not accessToken:
        raise Exception("Authorization header or token missing")

    # Extract token from header or cookies
    if auth_header:
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    elif accessToken:
        token = accessToken

    # Decode token
    decoded_token = decode_jwt_token(token)

    user_id = decoded_token.get('user_id')
    if not user_id:
        raise Exception("User ID not found in token")

    return user_id


@app.route('/protected', methods=['GET'])
def protected_route():
    try:
        user_id = verify_token()  # This will raise an exception if there's any error
        # Proceed with your logic (e.g., fetching user data)
        return jsonify({"message": f"Welcome, user {user_id}!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401


if __name__ == '__main__':
    app.run(debug=True)
