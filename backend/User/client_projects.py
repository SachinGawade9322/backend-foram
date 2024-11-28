from connection import get_db_connection
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Secret key for encoding the JWT
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  # Replace with your actual secret key

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

# Endpoint to create a new client project
def create_project():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    # Verify the token and extract the user_id
    user_id = verify_token()
    if isinstance(user_id, tuple):  # If `verify_token` returns a tuple, it's an error
        return user_id

    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()


    #fetch user details from db
    #then check the user account_type if it is freelancer return error
    if not user:
        return jsonify({"error" : "User not found ,Unauthorzed request"});

    if user[3] == "freelancer" :
        return jsonify({"error" : "Only clients can create project"});


    # Get data from the request
    data = request.get_json()
    domain = data.get('domain')
    title = data.get('title')
    description = data.get('description')
    skills = data.get('skills')  # Should be a list (array)
    proposal_document = data.get('proposal_document')
    project_deadline = data.get('project_deadline')
    work_type = data.get('work_type')
    price = data.get('price')

    # Validate required fields
    if not all([domain, title, description, skills, project_deadline, work_type, price]):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate work_type
    if work_type not in ['Hourly Rate', 'Fixed Rate']:
        return jsonify({"error": "Invalid work type. Must be 'HourlyRate' or 'FixedRate'."}), 400

    # Validate price
    if price < 5:
        return jsonify({"error": "Price must be at least $5"}), 400

  

    try:
        # Insert the project into the clientProject table
        cursor.execute("""
            INSERT INTO clientProjects (
                clientID, domain, title, description, skills, proposal_document, 
                project_deadline, work_type, price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING project_id;
        """, (
            user_id, domain, title, description, skills, proposal_document,
            project_deadline, work_type, price
        ))

        project_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "message": "Project created successfully",
            "project_id": project_id
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Failed to create project: {e}"}), 500

    finally:
        cursor.close()
        conn.close()


# Endpoint to retrieve all client projects for the logged-in user
def get_client_project_details():
    # Verify the token and extract the user_id
    user_id = verify_token()
    if isinstance(user_id, tuple):  # If `verify_token` returns a tuple, it's an error
        return user_id

    
    #fetch user details from db
    #then check the user account_type if it is freelancer return error


    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cursor = conn.cursor()

        # Retrieve projects for the logged-in user
        cursor.execute("SELECT * FROM clientProjects WHERE clientID = %s;", (user_id,))
        projects = cursor.fetchall()

        # Convert the result into a list of dictionaries
        project_list = []
        for project in projects:
            project_list.append({
                "project_id": project[0],
                "clientID": project[1],
                "domain": project[2],
                "description": project[3],
                "skills": project[4],
                "proposal_document": project[5],
                "work_type": project[6],
                "price": project[7],
                "project_deadline": project[8],
                "title": project[9]
            })

        return jsonify(project_list), 200

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve projects: {e}"}), 500

    finally:
        cursor.close()
        conn.close()


def get_client_project_by_id(project_id):

    user_id = verify_token()
    if isinstance(user_id, tuple):  # If `verify_token` returns a tuple, it's an error
        return user_id

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    print(project_id)

    try:
        cursor = conn.cursor()

        # Query to fetch the project by project_id
        cursor.execute("""
            SELECT project_id, clientID, domain, title, description, skills, 
                   proposal_document, project_deadline, work_type, price
            FROM clientProjects
            WHERE project_id = %s;
        """, (project_id,))

        project = cursor.fetchone()

        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Formatting the project data
        project_details = {
            "project_id": project[0],
            "clientID": project[1],
            "domain": project[2],
            "title": project[3],
            "description": project[4],
            "skills": project[5],
            "proposal_document": project[6],
            "project_deadline": project[7],
            "work_type": project[8],
            "price": project[9],
        }

        return jsonify({"project_details": project_details}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to fetch project details: {e}"}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
