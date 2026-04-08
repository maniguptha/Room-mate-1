from flask import Blueprint, request, jsonify
from extensions import db, calculate_distance
from models import Room, User
import jwt

matches_bp = Blueprint('matches', __name__)
SECRET_KEY = 'super-secret-staymatch-key-123'

def token_required(f):
    def decorator(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data['user_id']
        except Exception as e:
            return jsonify({'message': f'Token is invalid! {str(e)}'}), 401
        return f(user_id, *args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator

@matches_bp.route('/', methods=['GET'])
@token_required
def get_matches(user_id):
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', type=float, default=30.0)

    # Matches are now dynamically drawn from real users
    all_users = User.query.filter(User.id != user_id).all()
    
    matches_list = []
    for u in all_users:
        dist = None
        if lat is not None and lng is not None and u.latitude and u.longitude:
            dist = calculate_distance(lat, lng, u.latitude, u.longitude)
            if dist > radius:
                continue

        matches_list.append({
            "id": u.id,
            "name": u.name,
            "age": u.age or 25,
            "location": u.location or "Contact for location",
            "compatibility": 88, 
            "ai_pick": False,
            "budget": u.budget or "Flexible",
            "traits": u.traits.split(",") if u.traits else ["Quiet", "Clean"],
            "avatar_color": "violet",
            "profile_pic": u.profile_pic or "",
            "distance": round(dist, 1) if dist is not None else None
        })

    # Sort by compatibility, but if distance is present, maybe consider it?
    # For now, let's just sort by compatibility as before, but include distance.
    matches_list.sort(key=lambda x: x['compatibility'], reverse=True)

    return jsonify({
        "success": True,
        "matches": matches_list
    })

@matches_bp.route('/<int:match_id>', methods=['GET'])
@token_required
def get_match_detail(user_id, match_id):
    u = User.query.get(match_id)
    if not u:
        return jsonify({"success": False, "message": "User not found"}), 404
        
    return jsonify({"success": True, "roommate": {
        "id": u.id,
        "name": u.name,
        "age": u.age or 25,
        "location": u.location or "Contact for location",
        "compatibility": 88,
        "ai_pick": False,
        "budget": u.budget or "Flexible",
        "traits": u.traits.split(",") if u.traits else ["Quiet", "Clean"],
        "avatar_color": "violet",
        "profile_pic": u.profile_pic or "",
        "about": u.bio or "This user is looking for a roommate."
    }})
