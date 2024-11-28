import psycopg2
import os
from dotenv import load_dotenv
import logging

# Load the .env file and its contents
load_dotenv()

# Get the database URL from the .env file
database_url = os.getenv("DATABASE_URL")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        if not database_url:
            logger.error("Database URL not set.")
            return None

        # Connect to the database
        conn = psycopg2.connect(database_url)
        logger.info("Database connection to NeonDB is successful!")
        return conn

    except Exception as e:
        logger.error("Failed to connect to NeonDB.")
        logger.error(f"Error: {e}")
        return None