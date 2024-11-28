from utils.connection import get_db_connection

# Function to insert event registration details
def event_registration(user_id, firstname, lastname, email, mobile_no):
    conn = get_db_connection()
    if not conn:
        return False, "Failed to connect to the database"

    try:
        cursor = conn.cursor()
        
        # Insert the registration details into eventRegistration table
        cursor.execute("""
            INSERT INTO eventRegistration (user_id, firstname, lastname, email, mobile_no)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, firstname, lastname, email, mobile_no))
        
        conn.commit()
        return True, "Success"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        cursor.close()
        conn.close()

# Function to fetch user details from the database
def get_user_registration_details(user_id):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT firstname, lastname, email, mobile_no
            FROM users
            WHERE id = %s
        """, (user_id,))
        result = cursor.fetchone()

        if result:
            return {
                "firstname": result[0],
                "lastname": result[1],
                "email": result[2],
                "mobile_no": result[3]
            }
        return None

    except Exception:
        return None

    finally:
        cursor.close()
        conn.close()