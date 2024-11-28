from flask import request, jsonify
from utils.verify_token import verify_token
from models.event_registration_model import event_registration, get_user_registration_details
# Controller for event registration
def register_event():
    try:
        # Get the logged-in user's ID
        user_id = verify_token()
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Fetch user details from the database
        user_details = get_user_registration_details(user_id)
        if not user_details:
            return jsonify({"error": "User not found"}), 404

        # Extract user details
        firstname = user_details.get("firstname")
        lastname = user_details.get("lastname")
        email = user_details.get("email")
        mobile_no = user_details.get("mobile_no")

        # Call the model function to insert the data
        success, message = event_registration(user_id, firstname, lastname, email, mobile_no)
        if not success:
            return jsonify({"error": message}), 500

        return jsonify({"message": "Registration successful all details will be shared soon through email, Thank you!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
