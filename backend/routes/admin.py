from flask import Blueprint, request, jsonify, current_app, g
from middleware.auth_middleware import admin_required
from bson import ObjectId
from bson.errors import InvalidId
from utils import serialize_doc
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
@admin_required()
def get_stats():
    db = current_app.db
    total_resources = db.resources.count_documents({})
    active_bookings = db.bookings.count_documents({"status": {"$in": ["pending", "approved"]}})
    pending_staff = db.users.count_documents({"role": "staff", "account_status": "pending"})
    total_users = db.users.count_documents({})
    return jsonify({
        "total_resources": total_resources,
        "active_bookings": active_bookings,
        "pending_staff": pending_staff,
        "total_users": total_users
    }), 200

@admin_bp.route('/users', methods=['GET'])
@admin_required()
def get_users():
    role = request.args.get('role')
    query = {}
    if role:
        query['role'] = role
        
    db = current_app.db
    users = list(db.users.find(query, {"password": 0}))
    return jsonify(serialize_doc(users)), 200

@admin_bp.route('/staff/pending', methods=['GET'])
@admin_bp.route('/pending-staff', methods=['GET'])
@admin_required()
def get_pending_staff():
    db = current_app.db
    users = list(db.users.find({"role": "staff", "account_status": "pending"}, {"password": 0}))
    return jsonify(serialize_doc(users)), 200

@admin_bp.route('/staff/<user_id>/approve', methods=['PUT', 'PATCH'])
@admin_required()
def approve_staff(user_id):
    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({"error": "Invalid user ID"}), 400
        
    db = current_app.db
    db.users.update_one({"_id": obj_id}, {"$set": {"account_status": "active"}})
    updated_user = db.users.find_one({"_id": obj_id}, {"password": 0})
    return jsonify(serialize_doc(updated_user)), 200

@admin_bp.route('/staff/<user_id>/reject', methods=['PUT', 'PATCH'])
@admin_required()
def reject_staff(user_id):
    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({"error": "Invalid user ID"}), 400
        
    db = current_app.db
    db.users.update_one({"_id": obj_id}, {"$set": {"account_status": "rejected"}})
    updated_user = db.users.find_one({"_id": obj_id}, {"password": 0})
    return jsonify(serialize_doc(updated_user)), 200

@admin_bp.route('/users/<user_id>/role', methods=['PUT', 'PATCH'])
@admin_required()
def change_user_role(user_id):
    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({"error": "Invalid user ID"}), 400
        
    data = request.json or {}
    new_role = data.get('role')
    if new_role not in ['student', 'staff', 'admin']:
        return jsonify({"error": "Invalid role"}), 400
        
    db = current_app.db
    update_data = {"role": new_role}
    if new_role == 'staff':
        update_data["account_status"] = "active"
        
    db.users.update_one({"_id": obj_id}, {"$set": update_data})
    updated_user = db.users.find_one({"_id": obj_id}, {"password": 0})
    return jsonify(serialize_doc(updated_user)), 200

@admin_bp.route('/bookings', methods=['GET'])
@admin_required()
def get_admin_bookings():
    db = current_app.db
    status = request.args.get('status')
    query = {}
    if status:
        query['status'] = status
        
    bookings = list(db.bookings.find(query).sort("created_at", -1))
    for b in bookings:
        user = db.users.find_one({"_id": ObjectId(b['user_id'])}) if ObjectId.is_valid(b.get('user_id', '')) else None
        b['student_name'] = user['name'] if user else 'Unknown'
        b['student_reg_no'] = user.get('register_no', user.get('reg_no', '-')) if user else '-'
        b['user_name'] = b['student_name']
        
        resource = db.resources.find_one({"_id": ObjectId(b['resource_id'])}) if ObjectId.is_valid(b.get('resource_id', '')) else None
        b['resource_name'] = resource['name'] if resource else 'Unknown'
        b['resource_tier'] = resource.get('tier', 'standard') if resource else 'standard'
        
    return jsonify(serialize_doc(bookings)), 200

@admin_bp.route('/bookings/<booking_id>/status', methods=['PATCH', 'PUT'])
@admin_required()
def update_admin_booking_status(booking_id):
    try:
        obj_id = ObjectId(booking_id)
    except InvalidId:
        return jsonify({"error": "Invalid booking ID"}), 400
        
    data = request.json or {}
    new_status = data.get('status')
    if new_status not in ['approved', 'rejected']:
        return jsonify({"error": "Status must be approved or rejected"}), 400
        
    db = current_app.db
    db.bookings.update_one(
        {"_id": obj_id},
        {"$set": {"status": new_status, "approved_by": g.user_id}}
    )
    updated_booking = db.bookings.find_one({"_id": obj_id})
    return jsonify(serialize_doc(updated_booking)), 200

@admin_bp.route('/resources', methods=['POST'])
@admin_required()
def add_admin_resource():
    data = request.json or {}
    name = data.get('name')
    rtype = data.get('type')
    tier = data.get('tier', 'standard')
    location = data.get('location')
    capacity = data.get('capacity')
    
    if not all([name, rtype, location, capacity]):
        return jsonify({"error": "Missing required fields"}), 400
        
    db = current_app.db
    resource = {
        "name": name,
        "type": rtype,
        "tier": tier,
        "location": location,
        "capacity": int(capacity),
        "is_available": True,
        "created_at": datetime.utcnow()
    }
    result = db.resources.insert_one(resource)
    resource['_id'] = result.inserted_id
    return jsonify(serialize_doc(resource)), 201

@admin_bp.route('/resources/<resource_id>', methods=['PUT'])
@admin_required()
def update_admin_resource(resource_id):
    try:
        obj_id = ObjectId(resource_id)
    except InvalidId:
        return jsonify({"error": "Invalid resource ID"}), 400
        
    data = request.json or {}
    db = current_app.db
    update_fields = {}
    for key in ['name', 'type', 'tier', 'location', 'capacity', 'is_available']:
        if key in data:
            if key == 'capacity':
                update_fields[key] = int(data[key])
            else:
                update_fields[key] = data[key]
                
    db.resources.update_one({"_id": obj_id}, {"$set": update_fields})
    updated = db.resources.find_one({"_id": obj_id})
    return jsonify(serialize_doc(updated)), 200

@admin_bp.route('/resources/<resource_id>', methods=['DELETE'])
@admin_required()
def delete_admin_resource(resource_id):
    try:
        obj_id = ObjectId(resource_id)
    except InvalidId:
        return jsonify({"error": "Invalid resource ID"}), 400
        
    db = current_app.db
    db.resources.delete_one({"_id": obj_id})
    return jsonify({"message": "Resource deleted"}), 200
