from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from connection import get_db_connection
import os 
from flask_cors import CORS
import re
import jwt  

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes

# Secret key for encoding the JWT
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") # Replace with a strong secret key

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


def fetch_user_data():
    """
    Fetch user-specific project data (domain, work type, price) from the database 
    and return as individual variables.
    """
    # Verify the token and extract the user_id
    user_id = verify_token()
    if isinstance(user_id, tuple):  # If `verify_token` returns a tuple, it's an error
        return user_id
    
    conn = get_db_connection()
    if not conn:
        return None, None, None, "Failed to connect to database"

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT domain, work_type, price
            FROM clientprojects
            WHERE user_id = %s;
        """, (user_id,))
        records = cursor.fetchall()
        conn.close()

        # Extract data from the fetched records
        domains = [record[0] for record in records]
        work_types = [record[1] for record in records]
        prices = [record[2] for record in records]

        return domains, work_types, prices, None
    except Exception as e:
        conn.close()
        return None, None, None, str(e)

    
# Load the dataset
df = pd.read_csv('C://Users//Aakash//Desktop//NeuraFlow-Hack2Hire//backend//User//recommandation_system//dataset.csv')

# Fetch user-specific data
domains, work_types, prices, error = fetch_user_data()
if error:
    print(f"Error fetching user data: {error}")
else:
    # Prepare data for encoding and scaling
    # Combine the domains and work_types into a structure suitable for OneHotEncoder
    data = {'domain': domains, 'Type': work_types}
    
    # Step 1: Encode the categorical features (Domain, Type)
    x_col = ['domain', 'Type']
    encoder = OneHotEncoder(handle_unknown='ignore')
    encoded_skills = encoder.fit_transform(
        np.array([data['domain'], data['Type']]).T
    )

    # Step 2: Scale numerical features (Price)
    numerical_columns = ['Price']
    prices_array = np.array(prices).reshape(-1, 1)  # Ensure prices is a 2D array
    scaler = StandardScaler()
    scaled_numerical = scaler.fit_transform(prices_array)

    print("Encoded Skills:", encoded_skills.toarray())
    print("Scaled Numerical Features:", scaled_numerical)
    
# Step 3: Combine encoded categorical and numerical features
features = np.hstack((encoded_skills.toarray(), scaled_numerical))

# Load the pre-trained KMeans model
with open('C://Users//Aakash//Desktop//NeuraFlow-Hack2Hire//backend//User//recommandation_system//model.pkl', 'rb') as model_file:
    kmeans_model = pickle.load(model_file)
    
def recommend_projects(domain, freelancer_type, budget=None, top_n=5):
    """
    Recommends projects based on the user's domain expertise, freelancer type, and optional budget constraints.
    """
    # Step 1: Prepare user input for domain and type (matching the encoder used in training)
    user_data = pd.DataFrame({'Domain': domain, 'Type': [freelancer_type] * len(domain)})
    user_skill_vector = encoder.transform(user_data)  # Ensure same encoder as training

    # Step 2: Handle budget and numerical features
    user_budget = budget if budget else df['Price'].mean()
    user_numerical_features = np.array([[user_budget]])  # Single value
    user_numerical_features_scaled = scaler.transform(user_numerical_features)  # Ensure same scaler
    user_numerical_features_scaled = np.repeat(user_numerical_features_scaled, len(domain), axis=0)  # Match rows

    # Step 3: Combine encoded and scaled features
    user_features = np.hstack((user_skill_vector.toarray(), user_numerical_features_scaled))

    # Step 4: Compute cosine similarity
    similarities = cosine_similarity(features, user_features).mean(axis=1)  # Average across multiple inputs
    df['SimilarityScore'] = similarities  # Add similarity scores to the DataFrame

    # Step 5: Filter projects by budget, if specified
    if budget:
        matching_projects = df[df['Price'] <= budget]  # Only include projects within budget
    else:
        matching_projects = df  # Include all projects

    # Step 6: Sort by similarity score and select top recommendations
    recommendations = matching_projects.sort_values(by='SimilarityScore', ascending=False).head(top_n)

    return recommendations  # Return all information about the recommended projects

# Flask API route to recommend projects
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Parse input data
        data = request.json
        domain = data.get('domain', [])
        freelancer_type = data.get('freelancer_type', 'hourly')
        budget = data.get('budget', None)

        # Validate inputs
        if not domain:
            return jsonify({"error": "Domain is required"}), 400

        # Get recommendations
        recommendations = recommend_projects(domain, freelancer_type, budget)

        # Convert DataFrame to a JSON-compatible format
        recommendations_json = recommendations.to_dict(orient='records')

        # Return the recommendations as JSON
        return jsonify({"recommendations": recommendations_json})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)