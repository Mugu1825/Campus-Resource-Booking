from flask import Blueprint, request, jsonify, current_app, g
from middleware.auth_middleware import login_required, staff_required
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from config import Config
from utils import serialize_doc

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

@bookings_bp.route('/', methods=['GET'])
@login_required()
def get_bookings():
    db = current_app.db
    status = request.args.get('status')
    resource_id = request.args.get('resource_id')
    date_start = request.args.get('date_start')
    
    query = {}
    if status: query['status'] = status
    if resource_id: query['resource_id'] = resource_id
    if date_start: query['date_start'] = date_start
    
    # If student, strictly return own bookings
    if g.role == 'student':
        query['user_id'] = g.user_id
        
    bookings = list(db.bookings.find(query).sort("created_at", -1))
    
    for b in bookings:
        user = db.users.find_one({"_id": ObjectId(b['user_id'])}) if ObjectId.is_valid(b.get('user_id', '')) else None
        b['student_name'] = user['name'] if user else 'Unknown'
        b['student_reg_no'] = user.get('register_no', user.get('reg_no', '-')) if user else '-'
        b['user_name'] = b['student_name']
        
        resource = db.resources.find_one({"_id": ObjectId(b['resource_id'])}) if ObjectId.is_valid(b.get('resource_id', '')) else None
        b['resource_name'] = resource['name'] if resource else 'Unknown'
        b['resource_tier'] = resource.get('tier', 'standard') if resource else 'standard'
        
    if g.role == 'staff':
        bookings = [b for b in bookings if b.get('resource_tier') == 'standard']
        
    return jsonify(serialize_doc(bookings)), 200

@bookings_bp.route('/my', methods=['GET'])
@login_required()
def get_my_bookings():
    db = current_app.db
    bookings = list(db.bookings.find({"user_id": g.user_id}).sort("created_at", -1))
    
    for b in bookings:
        resource = db.resources.find_one({"_id": ObjectId(b['resource_id'])}) if ObjectId.is_valid(b.get('resource_id', '')) else None
        b['resource_name'] = resource['name'] if resource else 'Unknown'
        b['resource_tier'] = resource.get('tier', 'standard') if resource else 'standard'
        
    return jsonify(serialize_doc(bookings)), 200

@bookings_bp.route('/', methods=['POST'])
@login_required()
def create_booking():
    if g.role != 'student':
        return jsonify({"error": "Only students can create bookings"}), 403
        
    data = request.json or {}
    resource_id = str(data.get('resource_id') or '').strip()
    date_start = (data.get('date_start') or data.get('start_date') or '').strip()
    date_end = (data.get('date_end') or data.get('end_date') or date_start).strip()
    start_slot = (data.get('start_slot') or '').strip()
    end_slot = (data.get('end_slot') or '').strip()
    is_hackathon = bool(data.get('is_hackathon', False))
    hackathon_event = (data.get('hackathon_event') or data.get('event_name') or '').strip() or None
    
    if not all([resource_id, date_start, start_slot, end_slot]):
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        obj_resource_id = ObjectId(resource_id)
    except InvalidId:
        return jsonify({"error": "Invalid resource ID"}), 400
        
    db = current_app.db
    resource = db.resources.find_one({"_id": obj_resource_id})
    if not resource:
        return jsonify({"error": "Resource not found"}), 404
    if not resource.get('is_available'):
        return jsonify({"error": "Resource is not currently available for booking"}), 400
        
    if start_slot not in Config.TIME_SLOTS or end_slot not in Config.TIME_SLOTS:
        return jsonify({"error": "Invalid time slot selected"}), 400
        
    start_idx = Config.TIME_SLOTS.index(start_slot)
    end_idx = Config.TIME_SLOTS.index(end_slot)
    
    if end_idx <= start_idx:
        return jsonify({"error": "End slot must be after start slot"}), 400
        
    d_start = datetime.strptime(date_start, "%Y-%m-%d")
    d_end = datetime.strptime(date_end, "%Y-%m-%d")
    
    if not is_hackathon:
        if end_idx - start_idx > Config.MAX_REGULAR_SLOTS:
            return jsonify({"error": f"Regular bookings are limited to maximum {Config.MAX_REGULAR_SLOTS} hours"}), 400
        if date_start != date_end:
            return jsonify({"error": "Regular bookings must be on the same date"}), 400
    else:
        if not hackathon_event:
            return jsonify({"error": "Event name is required for hackathon bookings"}), 400
        if (d_end - d_start).days > 2:
            return jsonify({"error": "Hackathons cannot exceed 2 days duration"}), 400
            
    # Conflict check
    query = {
        "resource_id": str(obj_resource_id),
        "status": {"$in": ["pending", "approved"]}
    }
    existing_bookings = list(db.bookings.find(query))
    
    for b in existing_bookings:
        b_d_start = datetime.strptime(b['date_start'], "%Y-%m-%d")
        b_d_end = datetime.strptime(b['date_end'], "%Y-%m-%d")
        
        if d_start <= b_d_end and d_end >= b_d_start:
            if b.get('is_hackathon') or is_hackathon:
                return jsonify({"error": "Resource is already reserved for an event during these dates"}), 400
            else:
                if date_start == b['date_start']:
                    b_start_idx = Config.TIME_SLOTS.index(b['start_slot'])
                    b_end_idx = Config.TIME_SLOTS.index(b['end_slot'])
                    if start_idx < b_end_idx and end_idx > b_start_idx:
                        return jsonify({"error": f"Conflict: Slot overlaps with an existing booking ({b['start_slot']} - {b['end_slot']})"}), 400

    booking = {
        "user_id": g.user_id,
        "resource_id": str(obj_resource_id),
        "date_start": date_start,
        "date_end": date_end,
        "start_slot": start_slot,
        "end_slot": end_slot,
        "is_hackathon": is_hackathon,
        "hackathon_event": hackathon_event,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = db.bookings.insert_one(booking)
    return jsonify({"message": "Booking request submitted successfully", "booking_id": str(result.inserted_id)}), 201

@bookings_bp.route('/<booking_id>/approve', methods=['PUT', 'PATCH'])
@staff_required()
def approve_booking(booking_id):
    try:
        obj_id = ObjectId(booking_id)
    except InvalidId:
        return jsonify({"error": "Invalid booking ID"}), 400
        
    db = current_app.db
    booking = db.bookings.find_one({"_id": obj_id})
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
        
    resource = db.resources.find_one({"_id": ObjectId(booking['resource_id'])}) if ObjectId.is_valid(booking.get('resource_id', '')) else None
    
    if booking.get('is_hackathon') and g.role != 'admin':
        return jsonify({"error": "Only admins can approve hackathon bookings"}), 403
    if resource and resource.get('tier') == 'premium' and g.role != 'admin':
        return jsonify({"error": "Only admins can approve premium resource bookings"}), 403
        
    db.bookings.update_one(
        {"_id": obj_id},
        {"$set": {"status": "approved", "approved_by": g.user_id}}
    )
    
    updated_booking = db.bookings.find_one({"_id": obj_id})
    return jsonify({"booking": serialize_doc(updated_booking)}), 200

@bookings_bp.route('/<booking_id>/reject', methods=['PUT', 'PATCH'])
@staff_required()
def reject_booking(booking_id):
    try:
        obj_id = ObjectId(booking_id)
    except InvalidId:
        return jsonify({"error": "Invalid booking ID"}), 400
        
    db = current_app.db
    booking = db.bookings.find_one({"_id": obj_id})
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
        
    resource = db.resources.find_one({"_id": ObjectId(booking['resource_id'])}) if ObjectId.is_valid(booking.get('resource_id', '')) else None
    
    if booking.get('is_hackathon') and g.role != 'admin':
        return jsonify({"error": "Only admins can reject hackathon bookings"}), 403
    if resource and resource.get('tier') == 'premium' and g.role != 'admin':
        return jsonify({"error": "Only admins can reject premium resource bookings"}), 403
        
    db.bookings.update_one(
        {"_id": obj_id},
        {"$set": {"status": "rejected", "rejected_by": g.user_id}}
    )
    
    updated_booking = db.bookings.find_one({"_id": obj_id})
    return jsonify({"booking": serialize_doc(updated_booking)}), 200

@bookings_bp.route('/<booking_id>/status', methods=['PATCH', 'PUT'])
@staff_required()
def update_booking_status_generic(booking_id):
    data = request.json or {}
    new_status = data.get('status')
    if new_status == 'approved':
        return approve_booking(booking_id)
    elif new_status == 'rejected':
        return reject_booking(booking_id)
    else:
        return jsonify({"error": "Status must be approved or rejected"}), 400

@bookings_bp.route('/<booking_id>/cancel', methods=['PATCH', 'POST', 'DELETE'])
@bookings_bp.route('/<booking_id>', methods=['DELETE'])
@login_required()
def cancel_booking(booking_id):
    try:
        obj_id = ObjectId(booking_id)
    except InvalidId:
        return jsonify({"error": "Invalid booking ID"}), 400
        
    db = current_app.db
    booking = db.bookings.find_one({"_id": obj_id})
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
        
    if g.role == 'student':
        if booking['user_id'] != g.user_id:
            return jsonify({"error": "Cannot cancel other user's bookings"}), 403
        if booking['status'] != 'pending':
            return jsonify({"error": "Can only cancel pending bookings"}), 400
    elif g.role not in ['staff', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403
        
    db.bookings.update_one({"_id": obj_id}, {"$set": {"status": "cancelled"}})
    return jsonify({"message": "Booking cancelled"}), 200
