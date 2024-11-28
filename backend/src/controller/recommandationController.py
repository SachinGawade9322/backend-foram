from flask import request, jsonify
from utils.verify_token import verify_token
from models.recommandation_details_model import get_user_work_details ,get_recommendations


# Controller for getting recommendations
def get_user_recommendations():
    try:

        # Get the logged-in user's ID
        user_id = verify_token()
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        print(user_id)
        # Fetch user work details (domain, work_type, rate) from the database
        user_details = get_user_work_details(user_id)
        if not user_details:
            return jsonify({"error": "User details not found"}), 404

        domain = user_details.get("domain")
        
        # Pass the details to the recommendation model
        recommendations = get_recommendations(domain)
        if not recommendations:
            return jsonify({"message": "No recommendations found"}), 200

        return jsonify({"recommendations": recommendations}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500


