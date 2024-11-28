# src/models/service.py
from utils.connection import get_db_connection  # Adjust this based on your project structure
import cloudinary
import cloudinary.uploader

# Cloudinary configuration
cloudinary.config(
    cloud_name="dfggcfeqh",  
    api_key="883182657555187",
    api_secret="3QUAHA2IElK4xsthJhWz-W9_jaY",
    secure=True
)

@staticmethod
def create_service(user_id, title, category, sub_category, skills, pricing, description, faq, photo):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO userServices (user_id, title, category, sub_category, skills, pricing, description, faq, photo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, title, category, sub_category, skills, pricing, description, faq, photo))
    service_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return service_id

def service_images(file_data):
    try:
        upload_result = cloudinary.uploader.upload(file_data, folder="services")
        return upload_result.get('secure_url')
    except cloudinary.exceptions.Error as cloud_error:
        return f"Cloudinary upload failed: {str(cloud_error)}"
    except Exception as e:
        return f"Unexpected error occurred during upload: {str(e)}"
    
    
@staticmethod
def get_all_services():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services")
    services = cur.fetchall()
    cur.close()
    conn.close()
    return services