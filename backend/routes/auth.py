from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from config import Config
from datetime import datetime
from extensions import bcrypt
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.json or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    register_no = (data.get('register_no') or data.get('reg_no') or '').strip().upper()

    if not all([name, email, password, register_no]):
        return jsonify({"error": "Missing required fields"}), 400

    if not Config.REGISTER_NO_PATTERN.match(register_no):
        return jsonify({"error": "Invalid register number format. Example: 25CSE1011"}), 400

    department = register_no[2:5]
    db = current_app.db

    if db.users.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400
    if db.users.find_one({"register_no": register_no}):
        return jsonify({"error": "Register number already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "register_no": register_no,
        "department": department,
        "role": "student",
        "account_status": "active",
        "created_at": datetime.utcnow()
    }
    result = db.users.insert_one(user)
    return jsonify({"message": "Student registered successfully", "user_id": str(result.inserted_id)}), 201

@auth_bp.route('/register/staff', methods=['POST'])
def register_staff():
    data = request.json or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    department = (data.get('department') or '').strip().upper()

    if not all([name, email, password, department]):
        return jsonify({"error": "Missing required fields"}), 400

    if department not in Config.DEPARTMENTS:
        return jsonify({"error": f"Invalid department. Allowed: {', '.join(Config.DEPARTMENTS)}"}), 400

    db = current_app.db

    if db.users.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "department": department,
        "role": "staff",
        "account_status": "pending",
        "created_at": datetime.utcnow()
    }
    db.users.insert_one(user)
    return jsonify({"message": "Registration submitted. Awaiting admin approval."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db = current_app.db
    # Case-insensitive lookup for safety
    user = db.users.find_one({"email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}})

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid email or password"}), 401

    if user.get('account_status') == 'pending':
        return jsonify({"error": "Account awaiting admin approval"}), 403
    if user.get('account_status') == 'rejected':
        return jsonify({"error": "Account registration was rejected"}), 403

    user_id_str = str(user['_id'])
    claims = {
        "role": user['role'],
        "account_status": user.get('account_status', 'active'),
        "name": user['name'],
        "department": user.get('department')
    }
    token = create_access_token(identity=user_id_str, additional_claims=claims)

    return jsonify({
        "token": token,
        "role": user['role'],
        "name": user['name'],
        "user_id": str(user['_id']),
        "department": user.get('department')
    }), 200

@auth_bp.route('/departments', methods=['GET'])
def get_departments():
    return jsonify({"departments": Config.DEPARTMENTS}), 200
