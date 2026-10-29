from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config import Config
from datetime import datetime
from extensions import bcrypt
from bson import ObjectId
import re
import pyotp
import qrcode
import io
import base64

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
    totp_code = (data.get('totp_code') or '').strip()

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

    # Check Multi-Factor Authentication (TOTP)
    if user.get('is_mfa_enabled'):
        if not totp_code:
            return jsonify({
                "mfa_required": True,
                "email": user['email'],
                "message": "Two-factor authentication code required. Please enter 6-digit code from Google/Microsoft Authenticator."
            }), 200
        
        totp = pyotp.TOTP(user['totp_secret'])
        if not totp.verify(totp_code, valid_window=1):
            return jsonify({"error": "Invalid or expired 2FA code"}), 401

    user_id_str = str(user['_id'])
    claims = {
        "role": user['role'],
        "account_status": user.get('account_status', 'active'),
        "name": user['name'],
        "department": user.get('department'),
        "is_mfa_enabled": user.get('is_mfa_enabled', False)
    }
    token = create_access_token(identity=user_id_str, additional_claims=claims)

    return jsonify({
        "token": token,
        "role": user['role'],
        "name": user['name'],
        "user_id": str(user['_id']),
        "department": user.get('department'),
        "is_mfa_enabled": user.get('is_mfa_enabled', False)
    }), 200

@auth_bp.route('/2fa/setup', methods=['POST'])
@jwt_required()
def setup_2fa():
    user_id = get_jwt_identity()
    db = current_app.db
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=user['email'], issuer_name="CRBS Campus Booking")

    # Generate QR Code as base64
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

    # Store temp secret pending verification
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"temp_totp_secret": secret}})

    return jsonify({
        "secret": secret,
        "qr_code": qr_base64,
        "provisioning_uri": provisioning_uri,
        "message": "Scan QR code with Google Authenticator or Microsoft Authenticator, then verify with /2fa/verify"
    }), 200

@auth_bp.route('/2fa/verify', methods=['POST'])
@jwt_required()
def verify_2fa():
    user_id = get_jwt_identity()
    data = request.json or {}
    code = (data.get('totp_code') or data.get('code') or '').strip()

    if not code:
        return jsonify({"error": "6-digit TOTP code is required"}), 400

    db = current_app.db
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    temp_secret = user.get('temp_totp_secret')
    if not temp_secret:
        return jsonify({"error": "Please initiate 2FA setup first"}), 400

    totp = pyotp.TOTP(temp_secret)
    if not totp.verify(code, valid_window=1):
        return jsonify({"error": "Invalid verification code. Please check your authenticator app."}), 400

    # Activate MFA
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {"is_mfa_enabled": True, "totp_secret": temp_secret},
            "$unset": {"temp_totp_secret": ""}
        }
    )

    return jsonify({"message": "Multi-factor authentication (MFA) enabled successfully!", "is_mfa_enabled": True}), 200

@auth_bp.route('/2fa/disable', methods=['POST'])
@jwt_required()
def disable_2fa():
    user_id = get_jwt_identity()
    data = request.json or {}
    password = data.get('password')

    if not password:
        return jsonify({"error": "Password required to disable 2FA"}), 400

    db = current_app.db
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid password"}), 401

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {"is_mfa_enabled": False},
            "$unset": {"totp_secret": "", "temp_totp_secret": ""}
        }
    )
    return jsonify({"message": "2FA has been disabled"}), 200

@auth_bp.route('/departments', methods=['GET'])
def get_departments():
    return jsonify({"departments": Config.DEPARTMENTS}), 200
