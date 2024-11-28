from utils.connection import get_db_connection

# Function to apply for work and handle database logic
def apply_for_work(user_id, cover_letter, time_to_complete):
    
    if not isinstance(user_id, int):
        return {"error": "Invalid user ID provided"}, 400

    conn = get_db_connection()
    if not conn:
        return {"error": "Failed to connect to database"}, 500

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
            return {"error": "Insufficient connects or invalid user"}, 400

        remaining_connects = result[0]

        # Insert the application details into freelancerApplications
        cursor.execute("""
            INSERT INTO freelancerApplications (user_id, cover_letter, time_to_complete)
            VALUES (%s, %s, %s)
            RETURNING application_id;
        """, (user_id, cover_letter, time_to_complete))

        application_id = cursor.fetchone()[0]
        conn.commit()

        return {
            "message": "Application submitted successfully",
            "application_id": application_id,
            "remaining_connects": remaining_connects
        }, 201

    except Exception as e:
        conn.rollback()
        return {"error": f"Failed to submit application: {e}"}, 500

    finally:
        cursor.close()
        conn.close()
