import os
import getpass
from pymongo import MongoClient
from dotenv import load_dotenv
from extensions import bcrypt
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/campus_booking')

def seed_admin():
    client = MongoClient(MONGO_URI)
    db_name = MONGO_URI.split('/')[-1].split('?')[0]
    if not db_name or db_name == 'localhost:27017':
        db_name = 'campus_booking'
        
    db = client[db_name]
    
    existing_admin = db.users.find_one({"role": "admin"})
    if existing_admin:
        print("Admin user already exists.")
        return
        
    print("Creating admin user...")
    name = input("Enter admin name: ")
    email = input("Enter admin email: ")
    password = getpass.getpass("Enter admin password: ")
    
    from app import create_app
    app = create_app()
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
        admin_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": "admin",
            "account_status": "active",
            "created_at": datetime.utcnow()
        }
        
        db.users.insert_one(admin_user)
        print("\\nAdmin created successfully!")
        print(f"Email: {email}")
        print("Password: [hidden]")

if __name__ == '__main__':
    seed_admin()
