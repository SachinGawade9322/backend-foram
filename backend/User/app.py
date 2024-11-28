import jwt
from flask import Flask, request, jsonify
from authentication import register, login, logout # Assuming these are defined in authentication.py
from profile_update import update_user_details, get_user_details, update_profile_photo # Assuming these are defined in authentication.py
from freelancera_applications import apply_for_work
from client_projects import create_project, get_client_project_details,get_client_project_by_id
from recommandation import recommend
from flask_cors import CORS
app = Flask(__name__)
import os
CORS(app, supports_credentials=True)

# Secret key for encoding/decoding JWT tokens
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") 

# Register Route
@app.route('/register', methods=['POST'])
def register_route():
    # Calling the register function from authentication.py
    return register()

# Login Route
@app.route('/login', methods=['POST'])
def login_route():
    # Calling the login function from authentication.py
    return login()


# Logout Route
@app.route('/logout', methods=['POST'])
def logout_route():
    # Calling the Logout function from authentication.py
    return logout()


# update_user_details Route
@app.route('/update_user_details', methods=['POST'])
def update_user_details_route():
    # Calling the update_user_details function from profile_update.py
    return update_user_details()


# get_user_details Route
@app.route('/get_user_details', methods=['GET'])
def get_user_details_route():
    # Calling the get_user_details function from profile_update.py
    return get_user_details()


# update_profile_photo Route
@app.route('/update_profile_photo', methods=['POST'])
def update_profile_photo_route():
    # Calling the get_user_details function from profile_update.py
    return update_profile_photo()

# freelancer applications Route
@app.route('/apply', methods=['POST'])
def apply_for_work_route():
    return apply_for_work()

# client projects Route
@app.route('/create_project', methods=['POST'])
def create_project_route():
    return create_project()


# client projects details Route
@app.route('/get_project_details', methods=['GET'])
def get_project_details_route():
    return get_client_project_details()

@app.route('/get_project_details/<int:project_id>', methods=['GET'])
def get_project_details_id_route(project_id):
    return get_client_project_by_id(project_id)

@app.route('/recommend', methods=['POST'])
def recommandation_route(project_id):
    return recommend(project_id)

if __name__ == '__main__':
    app.run(debug=True)
