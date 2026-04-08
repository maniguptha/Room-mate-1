from flask import Blueprint, request, jsonify
from extensions import db
from models import User
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)
# bcrypt = Bcrypt() # Removed hashing as requested
SECRET_KEY = 'super-secret-staymatch-key-123'

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    email    = data.get('email', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    phone    = data.get('phone', '')

    if not email or not password or not full_name:
        return jsonify({"success": False, "message": "Name, email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered. Please login instead."}), 400

    # hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        name=full_name,
        email=email,
        password=password, # Use plain text
        phone=phone
    )
    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode({
        'user_id': new_user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "phone": new_user.phone or "",
            "location": "",
            "age": 0,
            "onboarding_complete": False
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    email    = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    # if user and bcrypt.check_password_hash(user.password, password):
    if user and user.password == password:
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone or "",
                "location": user.location or "",
                "age": user.age or 0,
                "onboarding_complete": bool(user.onboarding_complete)
            }
        }), 200

    return jsonify({"success": False, "message": "Invalid email or password. Please check and try again."}), 401

import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Replace with your actual SMTP config or env vars
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# Use an App Password if using Gmail, otherwise the user needs to set this up.
# For demo purposes we can leave dummy values but we'll try to catch exceptions.
SMTP_EMAIL = "staymatchsupport@gmail.com"  
SMTP_PASSWORD = "zlwl iymo lcvh atrx"   

def send_otp_email(to_email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = "StayMatch - Password Reset OTP"

        body = f"Your OTP for password reset is: {otp}\nThis OTP is valid for 10 minutes."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_EMAIL, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print("Failed to send email (SMTP might not be configured correctly):", e)
        # For development, we print the OTP to console so we can still test
        print(f"--- DEVELOPMENT OTP MOCK --- OTP for {to_email} is {otp}")
        return False

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    email = data.get('email', '').strip()
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if user:
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        user.reset_otp = otp
        user.reset_otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        db.session.commit()
        
        # Send Email
        send_otp_email(user.email, otp)
        
    # Always respond success so user can't enumerate emails
    return jsonify({"success": True, "message": "If this email exists, an OTP has been sent."})

@auth_bp.route('/verify-reset-otp', methods=['POST'])
def verify_reset_otp():
    data = request.json
    email = data.get('email', '').strip()
    otp = data.get('otp', '').strip()
    
    if not email or not otp:
        return jsonify({"success": False, "message": "Email and OTP are required"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "message": "Invalid email or OTP"}), 400
        
    if not user.reset_otp or user.reset_otp != otp:
        return jsonify({"success": False, "message": "Invalid OTP"}), 400
        
    if not user.reset_otp_expiry or user.reset_otp_expiry < datetime.datetime.utcnow():
        return jsonify({"success": False, "message": "OTP has expired. Please request a new one."}), 400
        
    return jsonify({"success": True, "message": "OTP verified successfully"})

@auth_bp.route('/update-password', methods=['POST'])
def update_password():
    data = request.json
    email = data.get('email', '').strip()
    otp = data.get('otp', '').strip()
    new_password = data.get('new_password', '')
    
    if not email or not otp or not new_password:
        return jsonify({"success": False, "message": "Email, OTP and new password are required"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user or user.reset_otp != otp or user.reset_otp_expiry < datetime.datetime.utcnow():
        return jsonify({"success": False, "message": "Invalid request or OTP expired"}), 400
        
    user.password = new_password
    user.reset_otp = None
    user.reset_otp_expiry = None
    db.session.commit()
    
    return jsonify({"success": True, "message": "Password updated successfully"})
