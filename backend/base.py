from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from flask_bcrypt import Bcrypt
import roadmap
import quiz
import generativeResources

api = Flask(__name__)
CORS(api)
bcrypt = Bcrypt(api)

# MySQL Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "your_password_here",  
    "database": "ai_learning_platform",
}


def get_db_connection():
    return mysql.connector.connect(**db_config)

# ======================= LOGIN ENDPOINT =======================
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
        return jsonify({"message": "Login successful", "user": user["username"]})
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# ======================= REGISTER ENDPOINT =======================
@api.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "User registered successfully"})
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409


# ======================= OTHER EXISTING ROUTES =======================
@api.route("/api/roadmap", methods=["POST"])
def get_roadmap():
    req = request.get_json()
    response_body = roadmap.create_roadmap(
        topic=req.get("topic", "Machine Learning"),
        time=req.get("time", "4 weeks"),
        knowledge_level=req.get("knowledge_level", "Absolute Beginner"),
    )
    return response_body


@api.route("/api/quiz", methods=["POST"])
def get_quiz():
    req = request.get_json()
    course = req.get("course")
    topic = req.get("topic")
    subtopic = req.get("subtopic")
    description = req.get("description")

    if not (course and topic and subtopic and description):
        return "Required Fields not provided", 400

    print("getting quiz...")
    response_body = quiz.get_quiz(course, topic, subtopic, description)
    return response_body


@api.route("/api/generate-resource", methods=["POST"])
def generative_resource():
    req = request.get_json()
    req_data = {
        "course": False,
        "knowledge_level": False,
        "description": False,
        "time": False,
    }
    for key in req_data.keys():
        req_data[key] = req.get(key)
        if not req_data[key]:
            return "Required Fields not provided", 400
    print(f"generative resources for {req_data['course']}")
    resources = generativeResources.generate_resources(**req_data)
    return resources


if __name__ == "__main__":
    api.run(debug=True)