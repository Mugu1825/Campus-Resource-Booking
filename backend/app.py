import os
import pymongo
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv

from config import Config
from extensions import bcrypt
from routes.auth import auth_bp
from routes.resources import resources_bp
from routes.bookings import bookings_bp
from routes.admin import admin_bp

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins='*')
    app.url_map.strict_slashes = False
    JWTManager(app)
    bcrypt.init_app(app)

    # Parse DB name from URI
    raw_uri = app.config['MONGO_URI']
    db_name = raw_uri.split('/')[-1]
    if '?' in db_name:
        db_name = db_name.split('?')[0]
    if not db_name or db_name in ('', 'localhost:27017'):
        db_name = 'campus_booking'

    try:
        client = MongoClient(raw_uri, serverSelectionTimeoutMS=5000)
        app.db = client[db_name]
    except Exception as e:
        print(f"Warning: Initial MongoDB connection deferred: {e}")
        class LazyDB:
            def __getattr__(self, name):
                try:
                    c = MongoClient(raw_uri, serverSelectionTimeoutMS=5000)
                    real_db = c[db_name]
                    app.db = real_db
                    return getattr(real_db, name)
                except Exception as inner_e:
                    raise RuntimeError(f"Database connection error: {inner_e}")
        app.db = LazyDB()

    # Defer index creation to first request so the app starts without a live DB
    _state = {'indexes_done': False}

    @app.before_request
    def ensure_indexes():
        if _state['indexes_done']:
            return
        try:
            app.db.users.create_index('email', unique=True)
            app.db.users.create_index('register_no', unique=True, sparse=True)
            app.db.resources.create_index('tier')
            app.db.resources.create_index('is_available')
            app.db.bookings.create_index('user_id')
            app.db.bookings.create_index('resource_id')
            app.db.bookings.create_index(
                [('resource_id', pymongo.ASCENDING),
                 ('date_start', pymongo.ASCENDING),
                 ('date_end', pymongo.ASCENDING)]
            )
            _state['indexes_done'] = True
        except Exception:
            pass  # Retry on next request if DB not yet reachable

    app.register_blueprint(auth_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(admin_bp)

    @app.after_request
    def add_instance_header(response):
        instance_id = os.getenv('INSTANCE_ID', os.uname().nodename)
        response.headers['X-Backend-Instance'] = instance_id
        return response

    @app.route('/api/health', methods=['GET'])
    def health_check():
        instance_id = os.getenv('INSTANCE_ID', os.uname().nodename)
        return jsonify({'status': 'ok', 'instance': instance_id}), 200

    @app.route('/api/instance', methods=['GET'])
    def get_instance():
        instance_id = os.getenv('INSTANCE_ID', os.uname().nodename)
        return jsonify({'instance': instance_id, 'status': 'ok'}), 200

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
