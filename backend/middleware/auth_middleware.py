from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def login_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_id = get_jwt_identity()
                
                if claims.get('account_status') != 'active':
                    return jsonify({"error": "Account is not active"}), 403
                    
                g.user_id = str(user_id)
                g.role = claims.get('role')
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": str(e)}), 401
        return decorator
    return wrapper

def staff_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_id = get_jwt_identity()
                
                if claims.get('account_status') != 'active':
                    return jsonify({"error": "Account is not active"}), 403
                    
                role = claims.get('role')
                if role not in ['staff', 'admin']:
                    return jsonify({"error": "Staff privileges required"}), 403
                    
                g.user_id = str(user_id)
                g.role = role
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": str(e)}), 401
        return decorator
    return wrapper

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_id = get_jwt_identity()
                
                if claims.get('account_status') != 'active':
                    return jsonify({"error": "Account is not active"}), 403
                    
                role = claims.get('role')
                if role != 'admin':
                    return jsonify({"error": "Admin privileges required"}), 403
                    
                g.user_id = str(user_id)
                g.role = role
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": str(e)}), 401
        return decorator
    return wrapper
