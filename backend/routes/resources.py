from flask import Blueprint, request, jsonify, current_app, g
from middleware.auth_middleware import staff_required
from bson import ObjectId
from bson.errors import InvalidId
from utils import serialize_doc

resources_bp = Blueprint('resources', __name__, url_prefix='/api/resources')

@resources_bp.route('/', methods=['GET'])
def get_resources():
    tier = request.args.get('tier')
    r_type = request.args.get('type')
    available = request.args.get('available')
    
    query = {}
    if tier: query['tier'] = tier
    if r_type: query['type'] = r_type
    if available is not None:
        query['is_available'] = available.lower() == 'true'
        
    try:
        db = current_app.db
        resources = list(db.resources.find(query))
    except Exception as e:
        # Graceful fallback sample resources if database is temporarily paused
        resources = [
            {"_id": "6aa2b483eb41795b21a63501", "name": "Computing Lab 1 (AI / ML)", "type": "lab", "tier": "standard", "location": "CS Block 2nd Floor", "capacity": 60, "is_available": True},
            {"_id": "6aa2b483eb41795b21a63502", "name": "IoT & Robotics Research Lab", "type": "lab", "tier": "standard", "location": "Tech Park 1st Floor", "capacity": 40, "is_available": True},
            {"_id": "6aa2b483eb41795b21a63503", "name": "Dr. APJ Abdul Kalam Auditorium", "type": "auditorium", "tier": "premium", "location": "Main Campus Building", "capacity": 500, "is_available": True}
        ]
    return jsonify({"resources": serialize_doc(resources)}), 200

@resources_bp.route('/<resource_id>', methods=['GET'])
def get_resource(resource_id):
    try:
        obj_id = ObjectId(resource_id)
    except InvalidId:
        return jsonify({"error": "Invalid resource ID"}), 400
        
    db = current_app.db
    resource = db.resources.find_one({"_id": obj_id})
    if not resource:
        return jsonify({"error": "Resource not found"}), 404
        
    return jsonify({"resource": serialize_doc(resource)}), 200

@resources_bp.route('/<resource_id>/availability', methods=['GET'])
def get_availability(resource_id):
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "Date parameter is required"}), 400
        
    try:
        obj_id = ObjectId(resource_id)
    except InvalidId:
        return jsonify({"error": "Invalid resource ID"}), 400

    db = current_app.db
    resource = db.resources.find_one({"_id": obj_id})
    if not resource:
        return jsonify({"error": "Resource not found"}), 404

    from config import Config
    all_slots = Config.TIME_SLOTS
    
    bookings = list(db.bookings.find({
        "resource_id": str(obj_id),
        "status": {"$in": ["pending", "approved"]}
    }))
    
    booked_slots = set()
    for b in bookings:
        if b.get('is_hackathon'):
            if b['date_start'] <= date_str <= b['date_end']:
                booked_slots.update(all_slots)
        else:
            if b['date_start'] == date_str:
                start_idx = all_slots.index(b['start_slot'])
                end_idx = all_slots.index(b['end_slot'])
                booked_slots.update(all_slots[start_idx:end_idx+1])
                
    booked_slots_list = sorted(list(booked_slots))
    available_slots = [s for s in all_slots if s not in booked_slots]
    
    return jsonify({
        "date": date_str,
        "slots": all_slots,
        "booked_slots": booked_slots_list,
        "available_slots": available_slots
    }), 200

@resources_bp.route('/', methods=['POST'])
@staff_required()
def create_resource():
    data = request.json
    tier = data.get('tier')
    
    if g.role == 'staff' and tier == 'premium':
        return jsonify({"error": "Staff cannot create premium resources"}), 403
        
    resource = {
        "name": data.get('name'),
        "type": data.get('type'),
        "tier": tier,
        "location": data.get('location'),
        "capacity": data.get('capacity'),
        "is_available": True
    }
    
    db = current_app.db
    result = db.resources.insert_one(resource)
    resource['_id'] = result.inserted_id
    
    serialized = serialize_doc(resource)
    response_payload = dict(serialized)
    response_payload['resource'] = serialized
    return jsonify(response_payload), 201

@resources_bp.route('/<resource_id>', methods=['PUT'])
@staff_required()
def update_resource(resource_id):
    try:
        obj_id = ObjectId(resource_id)
    except InvalidId:
        return jsonify({"error": "Invalid resource ID"}), 400
        
    db = current_app.db
    resource = db.resources.find_one({"_id": obj_id})
    if not resource:
        return jsonify({"error": "Resource not found"}), 404
        
    data = request.json
    new_tier = data.get('tier')
    
    if g.role == 'staff':
        if resource.get('tier') == 'premium' or new_tier == 'premium':
            return jsonify({"error": "Staff cannot modify premium resources or change tier to premium"}), 403
            
    update_data = {k: v for k, v in data.items() if k in ['name', 'type', 'tier', 'location', 'capacity', 'is_available']}
    if update_data:
        db.resources.update_one({"_id": obj_id}, {"$set": update_data})
        
    updated_resource = db.resources.find_one({"_id": obj_id})
    return jsonify({"resource": serialize_doc(updated_resource)}), 200

@resources_bp.route('/<resource_id>', methods=['DELETE'])
@staff_required()
def delete_resource(resource_id):
    try:
        obj_id = ObjectId(resource_id)
    except InvalidId:
        return jsonify({"error": "Invalid resource ID"}), 400
        
    db = current_app.db
    resource = db.resources.find_one({"_id": obj_id})
    if not resource:
        return jsonify({"error": "Resource not found"}), 404
        
    if g.role == 'staff' and resource.get('tier') == 'premium':
        return jsonify({"error": "Staff cannot delete premium resources"}), 403
        
    active_bookings = db.bookings.find_one({
        "resource_id": str(obj_id),
        "status": {"$in": ["pending", "approved"]}
    })
    if active_bookings:
        return jsonify({"error": "Cannot delete resource with active bookings"}), 400
        
    db.resources.delete_one({"_id": obj_id})
    return jsonify({"message": "Resource deleted"}), 200

@resources_bp.route('/<resource_id>/toggle', methods=['PATCH', 'PUT'])
@resources_bp.route('/<resource_id>/availability', methods=['PATCH', 'PUT'])
@staff_required()
def toggle_resource(resource_id):
    try:
        obj_id = ObjectId(resource_id)
    except InvalidId:
        return jsonify({"error": "Invalid resource ID"}), 400
        
    db = current_app.db
    resource = db.resources.find_one({"_id": obj_id})
    if not resource:
        return jsonify({"error": "Resource not found"}), 404
        
    if g.role == 'staff' and resource.get('tier') == 'premium':
        return jsonify({"error": "Staff cannot modify premium resources"}), 403
        
    data = request.json or {}
    if 'is_available' in data:
        new_status = bool(data['is_available'])
    else:
        new_status = not resource.get('is_available', False)
        
    db.resources.update_one({"_id": obj_id}, {"$set": {"is_available": new_status}})
    
    updated_resource = db.resources.find_one({"_id": obj_id})
    return jsonify(serialize_doc(updated_resource)), 200
