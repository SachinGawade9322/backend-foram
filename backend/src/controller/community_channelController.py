from flask import request, jsonify
from utils.verify_token import verify_token
from models.community_channel_model import create_post, get_all_posts, register_user, get_user_by_username
from utils.authentication import generate_token

def create_community_post():
    user_id = verify_token()
    if not user_id:
        return jsonify({"error": "User  not found"}), 401

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({"error": "Content is required"}), 400

    post_id = create_post(user_id, content)
    if not post_id:
        return jsonify({"error": "Failed to create post"}), 500

    return jsonify({"message": "Post created successfully", "post_id": post_id}), 201

def get_community_posts():
    posts = get_all_posts()
    if not posts:
        return jsonify({"error": "No posts found"}), 404

    return jsonify(posts), 200

def register_user_route():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user_id = register_user(username, password)
    if not user_id:
        return jsonify({"error": "Failed to register user"}), 500

    return jsonify({"message": "User  registered successfully", "user_id": user_id}), 201

def login_user_route():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = get_user_by_username(username)
    if not user or user[1] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user[0]) 
    return jsonify({"message": "Login successful", "token": token}), 200