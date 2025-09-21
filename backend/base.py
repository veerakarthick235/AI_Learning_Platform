import os
import jwt
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import mysql.connector
from dotenv import load_dotenv

# Import your custom modules for AI logic
import roadmap
import quiz
import generativeResources

# --- APP INITIALIZATION & CONFIGURATION ---

# Load environment variables from a .env file
load_dotenv()

api = Flask(__name__)
bcrypt = Bcrypt(api)

# Configure the secret key for JWT
api.config['SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "a_default_fallback_secret_key")

# Configure CORS to allow requests from your frontend
# The allowed origins are loaded from the .env file
cors_origins = os.getenv("CORS_ORIGINS", "https://ai-learning-portal.netlify.app/").split(',')
CORS(api, origins=cors_origins)

# MySQL Configuration using Environment Variables
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "ai_learning_platform"),
}

# --- HELPER FUNCTIONS ---

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# --- AUTHENTICATION DECORATOR ---

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            # Expected format: "Bearer <token>"
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Authentication token is missing!'}), 401

        try:
            data = jwt.decode(token, api.config['SECRET_KEY'], algorithms=["HS256"])
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
            current_user = cursor.fetchone()
            cursor.close()
            conn.close()
            if not current_user:
                 return jsonify({'message': 'User not found!'}), 401
        except Exception as e:
            return jsonify({'message': f'Token is invalid or expired! {e}'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# ======================= AUTHENTICATION ROUTES =======================

@api.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "User registered successfully"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500


@api.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and bcrypt.check_password_hash(user["password"], password):
        # Generate JWT token
        token = jwt.encode({
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(hours=24) # Token expires in 24 hours
        }, api.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({"message": "Login successful", "token": token})
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# ======================= PROTECTED ROUTES =======================

@api.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    profile_data = {
        "username": current_user['username'],
        "created_at": current_user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify(profile_data)

# ======================= FEATURE ROUTES =======================

@api.route("/api/roadmap", methods=["POST"])
@token_required
def get_roadmap(current_user):
    req = request.get_json()
    response_body = roadmap.create_roadmap(
        topic=req.get("topic", "Machine Learning"),
        time=req.get("time", "4 weeks"),
        knowledge_level=req.get("knowledge_level", "Absolute Beginner"),
    )
    return jsonify(response_body)


@api.route("/api/quiz", methods=["POST"])
@token_required
def get_quiz_route(current_user): # Renamed to avoid conflict with imported module
    req = request.get_json()
    response_body = quiz.get_quiz(
        course=req.get("course"),
        topic=req.get("topic"),
        subtopic=req.get("subtopic"),
        description=req.get("description"),
    )
    return jsonify(response_body)


@api.route("/api/generate-resource", methods=["POST"])
@token_required
def generative_resource_route(current_user): # Renamed to avoid conflict
    req = request.get_json()
    resources = generativeResources.generate_resources(
        course=req.get("course"),
        knowledge_level=req.get("knowledge_level"),
        description=req.get("description"),
        time=req.get("time"),
    )
    return jsonify(resources)

# Note: The chatbot endpoint is often left public, but you can add @token_required if needed.
@api.route('/api/chatbot', methods=['POST'])
def handle_chatbot():
    # ... (chatbot logic from previous answer) ...
    # This assumes you have a chatbot.py module or the logic here
    pass


# ======================= MAIN EXECUTION =======================

if __name__ == "__main__":
    # Use port 5000 for local development
    api.run(debug=True, port=5000)
