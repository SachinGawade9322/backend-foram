import json
from utils.connection import get_db_connection
import cloudinary
import cloudinary.uploader

# Cloudinary configuration
cloudinary.config(
    cloud_name="dfggcfeqh",  
    api_key="883182657555187",
    api_secret="3QUAHA2IElK4xsthJhWz-W9_jaY",
    secure=True
)

def get_user_from_db(user_id):
    conn = get_db_connection()
    if not conn:
        return "Database connection failed"
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user:
        return "User not found"
    
    return user


def update_user_in_db(user_id, update_query, update_values):
    conn = get_db_connection()
    if not conn:
        return "Database connection failed"
    
    cur = conn.cursor()
    cur.execute(update_query, update_values)
    conn.commit()
    cur.close()
    conn.close()
    
    return None


def upload_profile_photo(file_data):
    try:
        upload_result = cloudinary.uploader.upload(file_data, folder="profilePhoto")
        return upload_result.get('secure_url')
    except cloudinary.exceptions.Error as cloud_error:
        return f"Cloudinary upload failed: {str(cloud_error)}"
    except Exception as e:
        return f"Unexpected error occurred during upload: {str(e)}"

def fetch_user_by_id(user_id):
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}, 500

    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            return None
        user_details = {
            "id": user[0],
            "firstname": user[1],
            "lastname": user[2],
            "account_type": user[3],
            "email": user[4],
            "mobile_no": user[5],
            "profile_photo": user[7],
            "country": user[8],
            "working_domain": user[9],
            "technical_skills": user[10],
            "work_experience": user[11],
            "educational_details": user[12],
            "hourly_rate": user[13],
            "social_media_links": user[14],
            "connects": user[15],
            "bio": user[16]
        }
        return user_details
    except Exception as e:
        print(f"Error fetching user: {e}")
        return {"error": "Internal server error"}, 500
    finally:
        cur.close()
        conn.close()