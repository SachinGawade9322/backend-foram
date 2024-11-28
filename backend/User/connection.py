import psycopg2
import os
from dotenv import load_dotenv

# Load the .env file and its contents
load_dotenv()

# Get the database URL from the .env file
database_url = os.getenv("DATABASE_URL")

# print("Database URL:", database_url)

def get_db_connection():
    try:
        if not database_url:
            print("Error: Database URL not set.")
            return None

        # Connect to NeonDB using the connection string with sslmode=require
        conn = psycopg2.connect(database_url)
        
        print("Database connection to NeonDB is successful!")
        return conn

    except Exception as e:
        print("Failed to connect to NeonDB.")
        print(f"Error: {e}")
        return None
