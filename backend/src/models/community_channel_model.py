from utils.connection import get_db_connection

def create_post(user_id, content):
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO community_posts (user_id, content)
            VALUES (%s, %s) RETURNING post_id;
        """, (user_id, content))

        post_id = cursor.fetchone()[0]
        conn.commit()
        return post_id
    except Exception as e:
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_posts():
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT post_id, user_id, content FROM community_posts;")
        posts = cursor.fetchall()

        post_list = []
        for post in posts:
            post_list.append({
                "post_id": post[0],
                "user_id": post[1],
                "content": post[2]
            })

        return post_list
    except Exception as e:
        return None
    finally:
        cursor.close()
        conn.close()

def register_user(username, password):
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (%s, %s) RETURNING user_id;
        """, (username, password))

        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except Exception as e:
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, password FROM users WHERE username = %s;", (username,))
        return cursor.fetchone()
    except Exception as e:
        return None
    finally:
        cursor.close()
        conn.close()