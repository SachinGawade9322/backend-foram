import jwt
import json
import os
from flask import Flask, request, jsonify
from connection import get_db_connection
import cloudinary
import cloudinary.uploader
from werkzeug.datastructures import ImmutableMultiDict

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  # Replace with your actual secret key

# Cloudinary configuration
cloudinary.config(
    cloud_name="dfggcfeqh",  # Replace with your Cloudinary cloud name
    api_key="883182657555187",        # Replace with your Cloudinary API key
    api_secret="3QUAHA2IElK4xsthJhWz-W9_jaY",   # Replace with your Cloudinary API secret
    sercure=True
)

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


def update_user_details():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cur = conn.cursor()

    user_id = verify_token()
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400
    
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        return jsonify({"error": "Unauthorized request"}), 404
    
    
    data = request.json
    
    update_fields = []
    update_values = []

    if 'profilePhoto' in data:
        update_fields.append("profile_photo = %s")
        update_values.append(data['profilePhoto'])
    if 'firstName' in data:
        update_fields.append("firstname = %s")
        update_values.append(data['firstName'])
    if 'lastName' in data:
        update_fields.append("lastname = %s")
        update_values.append(data['lastName'])
    if 'mobileNo' in data:
        update_fields.append("mobile_no = %s")
        update_values.append(data['mobileNo'])
    if 'country' in data:
        update_fields.append("country = %s")
        update_values.append(data['country'])
    if 'workingDomain' in data:
        update_fields.append("working_domain = %s")
        update_values.append(data['workingDomain'])
    if 'technicalSkills' in data:
        update_fields.append("technical_skills = %s")
        update_values.append(data['technicalSkills'])
    if 'workExperience' in data:
        update_fields.append("work_experience = %s")
        update_values.append(json.dumps(data['workExperience']))
    if 'educationalDetails' in data:
        update_fields.append("educational_details = %s")
        update_values.append(json.dumps(data['educationalDetails']))
    if 'hourlyRate' in data:
        update_fields.append("hourly_rate = %s")
        update_values.append(data['hourlyRate'])
    if 'socialMediaLinks' in data:
        update_fields.append("social_media_links = %s")
        update_values.append(json.dumps(data['socialMediaLinks']))


    if update_fields:
        update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        update_values.append(user_id)
        cur.execute(update_query, update_values)
        conn.commit()

    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    updated_user = cur.fetchone()
    cur.close()
    conn.close()

    user_details = {
        "id": updated_user[0],
        "firstname": updated_user[1],
        "lastname": updated_user[2],
        "account_type": updated_user[3],
        "email": updated_user[4],
        "mobile_no": updated_user[5],
        "profile_photo": updated_user[7],
        "country": updated_user[8],
        "working_domain": updated_user[9],
        "technical_skills": updated_user[10],
        "work_experience": updated_user[11],
        "educational_details": updated_user[12],
        "hourly_rate": updated_user[13],
        "social_media_links": updated_user[14],
        "connects": updated_user[15]
    }

    return jsonify({"message": "User details updated successfully", "user": user_details}), 200

# Route to get user details
@app.route('/get_user', methods=['GET'])
def get_user_details():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cur = conn.cursor()

   
    user_id = verify_token()
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400

    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    cur.close()
    conn.close()

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

    return jsonify({"user": user_details}), 200


# Route to get user details
@app.route('/update_profile_photo', methods=['POST'])
def update_profile_photo():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cur = conn.cursor()

    user_id = verify_token()
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400


    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.files['profilePhoto']
    print(data)

    # Upload file to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(data, folder="profilePhoto")
        # Extract the URL from the upload result
        photo_url = upload_result.get('secure_url')

        # Log or store the uploaded file URL for debugging or further use
        print(f"Photo uploaded successfully: {photo_url}")
        
        if not photo_url :
            return jsonify({'error':'faild to upload profile photo'}), 500
        
        # Update the database with the new photo URL
        update_query = "UPDATE users SET profile_photo = %s WHERE id = %s"
        cur.execute(update_query, (photo_url, user_id))
        conn.commit()
        
    except cloudinary.exceptions.Error as cloud_error:
        return jsonify({"error": f"Cloudinary upload failed: {str(cloud_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error occurred during upload: {str(e)}"}), 500
    
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    updated_user = cur.fetchone()

    cur.close()
    conn.close()

    user_details = {
        "id": updated_user[0],
        "firstname": updated_user[1],
        "lastname": updated_user[2],
        "account_type" : updated_user[3],
        "email" : updated_user[4],
        "mobile_no": updated_user[5],
        "profile_photo" : updated_user[7],
        "country": updated_user[8],
        "working_domain": updated_user[9],
        "technical_skills": updated_user[10],
        "work_experience": updated_user[11],
        "educational_details": updated_user[12],
        "hourly_rate": updated_user[13],
        "social_media_links": updated_user[14],
        "connects": updated_user[15]
    }

    return jsonify({"user": user_details}), 200

if __name__ == '__main__':
    app.run(debug=True)
