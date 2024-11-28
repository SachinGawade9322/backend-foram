from utils.connection import get_db_connection
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Function to fetch user work details from the database
def get_user_work_details(user_id):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT working_domain
            FROM users
            WHERE id = %s
        """, (user_id,))
        result = cursor.fetchone()

        if result:
            return {"domain": result[0]}
        return None

    except Exception as e:
        print(f"Database error: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

# Function to get recommendations based on domain
def get_recommendations(domain, top_n=5):
    try:
        # Load the dataset
        df = pd.read_csv('C://Users//Aakash//Desktop//NeuraFlow-Hack2Hire//backend//User//recommandation_system//dataset.csv')

        if df.empty:
            return {"error": "Dataset is empty."}

        # Step 1: Encode the domain feature
        encoder = OneHotEncoder(handle_unknown='ignore')
        domain_encoded = encoder.fit_transform(df[['Domain']])  # Encode domains in the dataset

        # Transform user domain into the same encoded format
        user_domain_vector = encoder.transform([[domain]])

        # Step 2: Compute cosine similarity
        similarities = cosine_similarity(domain_encoded, user_domain_vector).flatten()

        # Add similarity scores to the DataFrame
        df['SimilarityScore'] = similarities

        # Step 3: Sort by similarity score and select top recommendations
        recommendations = df.sort_values(by='SimilarityScore', ascending=False).head(top_n)

        if recommendations.empty:
            return {"error": "No recommendations found."}

        return recommendations.to_dict(orient='records')  # Convert DataFrame to a dictionary list

    except Exception as e:
        return {"error": f"An error occurred: {e}"}
