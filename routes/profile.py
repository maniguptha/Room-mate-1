from flask import Blueprint, request, jsonify
from extensions import db
from models import User, Wishlist
from routes.matches import token_required

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET'])
@token_required
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    saved_count = Wishlist.query.filter_by(user_id=user_id).count()

    # Matches count = total other registered users, same source as the /api/matches/ endpoint
    matches_count = User.query.filter(User.id != user_id).count()

    # AI Score: 75 if onboarding is complete, 0 otherwise
    ai_score = 75 if user.onboarding_complete else 0

    return jsonify({
        "success": True,
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone or "",
        "location": user.location or "",
        "bio": user.bio or "",
        "age": user.age or 0,
        "budget": user.budget or "",
        "ai_score": ai_score,
        "matches": matches_count,
        "saved": saved_count,
        "traits": (user.traits.split(',') if user.traits else []),
        "profile_pic": user.profile_pic or "",
        "latitude": user.latitude or 0.0,
        "longitude": user.longitude or 0.0
    })

@profile_bp.route('/', methods=['PUT'])
@token_required
def update_profile(user_id):
    data = request.json
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    user.name     = data.get('name', user.name)
    user.phone    = data.get('phone', user.phone)
    user.location = data.get('location', user.location)
    user.bio      = data.get('bio', user.bio)
    user.age      = data.get('age', user.age)
    user.budget   = data.get('budget', user.budget)
    user.latitude = data.get('latitude', user.latitude)
    user.longitude = data.get('longitude', user.longitude)

    traits = data.get('traits')
    if isinstance(traits, list):
        user.traits = ",".join(traits)

    db.session.commit()
    return jsonify({"success": True, "message": "Profile updated successfully"})

import os
import uuid
from flask import current_app

@profile_bp.route('/picture', methods=['POST'])
@token_required
def upload_profile_picture(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.webp'}:
        return jsonify({"success": False, "message": "Invalid file format"}), 400

    upload_dir = os.path.join(current_app.root_path, 'uploads', 'profiles')
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"profile_{user_id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    user.profile_pic = f"/uploads/profiles/{filename}"
    db.session.commit()

    return jsonify({"success": True, "profile_pic": user.profile_pic})
