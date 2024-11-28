import os
from flask import Flask
from flask_cors import CORS
from utils.authentication import login, logout, register
from controller.profile_UpdateController import get_user_details, update_profile_photo, update_user_details
from controller.client_ProjectsController import create_client_project, get_client_projects_controller, get_client_project_by_id__controller
from controller.freelancer_ApplicationsController import apply_for_work_controller
from controller.event_RegistrationController import register_event
from controller.recommandationController import get_user_recommendations
from controller.servicesController import add_services_controller, get_all_services
from controller.community_channelController import create_community_post, get_community_posts, register_user_route, login_user_route

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Secret key for encoding/decoding JWT tokens
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") 

# Register Route
@app.route('/register', methods=['POST'])
def register_route():
    return register()

# Login Route
@app.route('/login', methods=['POST'])
def login_route():
    return login()

# Logout Route
@app.route('/logout', methods=['POST'])
def logout_route():
    return logout()

# User Details Route
@app.route('/get_user_details', methods=['GET'])
def get_user_details_route():
    return get_user_details()

# Update User Details Route
@app.route('/update_user_details', methods=['POST'])
def update_user_details_route():
    return update_user_details()

# Update Profile Photo Route
@app.route('/update_profile_photo', methods=['POST'])
def update_profile_photo_route():
    return update_profile_photo()

# Create Client Project Route
@app.route('/create_client_project', methods=['POST'])
def create_client_project_route():
    return create_client_project()

# Get Client Projects Route
@app.route('/get_client_projects', methods=['GET'])
def get_client_projects_route():
    return get_client_projects_controller()

# Get Client Project by ID Route
@app.route('/get_client_project_by_id/<int:project_id>', methods=['GET'])
def get_client_project_by_id_route(project_id):
    return get_client_project_by_id__controller(project_id)

# Apply for Work Route
@app.route('/apply_for_work', methods=['POST'])
def apply_for_work_controller_route():
    return apply_for_work_controller()

# Event Registration Route
@app.route('/event_registration', methods=['POST'])
def event_registration_route():
    return register_event()

# Get User Recommendations Route
@app.route('/get_user_recommendations', methods=['GET'])
def get_user_recommendations_route():
    return get_user_recommendations()

# Add Services Route
@app.route('/add_services', methods=['POST'])
def add_services_route():
    return add_services_controller()

# Get All Services Route
@app.route('/get_all_services', methods=['GET'])
def get_all_services_route():
    return get_all_services()

# Community Registration Route
@app.route('/community/register', methods=['POST'])
def community_register_route():
    return register_user_route()

# Community Login Route
@app.route('/community/login', methods=['POST'])
def community_login_route():
    return login_user_route()

# Create Community Post Route
@app.route('/community/create_post', methods=['POST'])
def create_community_post_route():
    return create_community_post()

# Get Community Posts Route
@app.route('/community/get_posts', methods=['GET'])
def get_community_posts_route():
    return get_community_posts()

if __name__ == '__main__':
    app.run(debug=True)