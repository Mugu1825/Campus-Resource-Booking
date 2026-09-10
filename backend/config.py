import os
import re
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/campus_booking')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or os.getenv('JWT_SECRET', 'super-secret-campus-resource-booking-jwt-key-32chars-min-2025!')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    
    DEPARTMENTS = ['CSE', 'ECE', 'EEE', 'MEE', 'INT', 'CIV', 'CHE', 'AER', 'BIO', 'MBA', 'MCA']
    REGISTER_NO_PATTERN = re.compile(r'^\d{2}(CSE|ECE|EEE|MEE|INT|CIV|CHE|AER|BIO|MBA|MCA)\d{4}$')
    TIME_SLOTS = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']
    
    MAX_REGULAR_SLOTS = 4
    MAX_HACKATHON_HOURS = 48
