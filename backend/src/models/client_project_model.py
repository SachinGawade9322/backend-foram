from utils.connection import get_db_connection

# Function to create a new client project
def create_project(user_id, domain, title, description, skills, proposal_document, project_deadline, work_type, price, connects, level):
    conn = get_db_connection()
    if not conn:
        return   "Failed to connect to database"

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO clientProjects (
                clientID, domain, title, description, skills, proposal_document, 
                project_deadline, work_type, price, connects, level
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING project_id;
        """, (user_id, domain, title, description, skills, proposal_document, project_deadline, work_type, price, connects, level))

        project_id = cursor.fetchone()[0]
        conn.commit()

        return project_id,  
    except Exception as e:
        conn.rollback()
        return   f"Failed to create project: {str(e)}"
    finally:
        cursor.close()
        conn.close()

# Function to get all client projects
def get_client_projects(user_id):
    conn = get_db_connection()
    if not conn:
        return   "Failed to connect to database"

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientProjects WHERE clientID = %s;", (user_id,))
        projects = cursor.fetchall()

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
                "title": project[9],
                "connects": project[10],
                "level": project[11]
            })

        return project_list,  
    except Exception as e:
        return   f"Failed to retrieve projects: {str(e)}"
    finally:
        cursor.close()
        conn.close()

# Function to get a project by ID
def get_client_project_by_id(project_id):
    conn = get_db_connection()
    if not conn:
        return   "Failed to connect to database"

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT project_id, clientID, domain, title, description, skills, 
                   proposal_document, project_deadline, work_type, price
            FROM clientProjects
            WHERE project_id = %s;
        """, (project_id,))

        project = cursor.fetchone()

        if not project:
            return   "Project not found"

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
            "connects": project[10],
            "level": project[11]
        }

        return project_details,  
    except Exception as e:
        return   f"Failed to fetch project details: {str(e)}"
    finally:
        cursor.close()
        conn.close()
