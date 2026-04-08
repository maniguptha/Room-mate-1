from flask import Blueprint, request, jsonify
from extensions import db, calculate_distance
from models import Room, Wishlist, RoomRating
from routes.matches import token_required
import os, json, uuid, math
from werkzeug.utils import secure_filename

rooms_bp = Blueprint('rooms', __name__)

UPLOAD_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads', 'rooms')
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def room_to_dict(r, wishlisted_ids=None):
    photos = []
    try:
        photos = json.loads(r.photos) if r.photos else []
    except Exception:
        pass
        
    ratings = RoomRating.query.filter_by(room_id=r.id).all()
    rating_count = len(ratings)
    avg_rating = sum(rt.rating for rt in ratings) / rating_count if rating_count > 0 else 0.0
    return {
        "id": r.id,
        "posted_by": r.posted_by,
        "title": r.title,
        "location": r.location,
        "price": r.price,
        "score": r.score,
        "ai_score": r.ai_score or 0,
        "ai_hygiene": r.ai_hygiene or 0,
        "ai_safety": r.ai_safety or 0,
        "ai_lifestyle": r.ai_lifestyle or 0,
        "ai_feedback": r.ai_feedback or "",
        "gradient_color": r.gradient_color,
        "description": r.description or "",
        "amenities": r.amenities.split(',') if r.amenities else [],
        "photos": photos,
        "room_type": r.room_type or "",
        "furnishing": r.furnishing or "",
        "ai_insight": r.ai_feedback or "",
        "latitude": r.latitude,
        "longitude": r.longitude,
        "is_wishlisted": (r.id in wishlisted_ids) if wishlisted_ids is not None else False,
        "avg_rating": round(avg_rating, 1),
        "rating_count": rating_count
    }

@rooms_bp.route('/', methods=['GET'])
@token_required
def get_rooms(user_id):
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', type=float, default=30.0) # km

    rooms = Room.query.all()
    wishlisted_ids = {w.room_id for w in Wishlist.query.filter_by(user_id=user_id).all()}
    
    result = []
    for r in rooms:
        d = room_to_dict(r, wishlisted_ids)
        if lat is not None and lng is not None:
            dist = calculate_distance(lat, lng, r.latitude, r.longitude)
            if dist <= radius:
                d['distance'] = round(dist, 1)
                result.append(d)
        else:
            result.append(d)

    # Sort by distance if filters applied
    if lat is not None and lng is not None:
        result.sort(key=lambda x: x.get('distance', 9999))

    return jsonify({"success": True, "rooms": result})

@rooms_bp.route('/', methods=['POST'])
@token_required
def create_room(user_id):
    data = request.json or {}
    new_room = Room(
        posted_by=user_id,
        title=data.get('title', 'New Room'),
        location=data.get('location', 'Unknown Location'),
        price=data.get('price', '₹10,000'),
        score=data.get('ai_score', 8.0),  # store overall AI score here too
        gradient_color=data.get('gradient_color', 'blue'),
        description=data.get('description', ''),
        amenities=','.join(data.get('amenities', [])),
        photos=json.dumps(data.get('photos', [])),
        ai_score=data.get('ai_score', 0.0),
        ai_hygiene=data.get('ai_hygiene', 0),
        ai_safety=data.get('ai_safety', 0),
        ai_lifestyle=data.get('ai_lifestyle', 0),
        ai_feedback=data.get('ai_feedback', ''),
        room_type=data.get('room_type', ''),
        furnishing=data.get('furnishing', ''),
        latitude=data.get('latitude', 0.0),
        longitude=data.get('longitude', 0.0)
    )
    db.session.add(new_room)
    db.session.commit()
    return jsonify({"success": True, "message": "Room listed successfully!", "room_id": new_room.id}), 201

@rooms_bp.route('/upload-photo', methods=['POST'])
@token_required
def upload_room_photo(user_id):
    """Upload a single room photo. Returns the accessible URL."""
    if 'photo' not in request.files:
        return jsonify({"success": False, "message": "No photo in request"}), 400
    file = request.files['photo']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid file type"}), 400
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"room_{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    file.save(os.path.join(UPLOAD_DIR, filename))
    url = f"/uploads/rooms/{filename}"
    return jsonify({"success": True, "url": url})

@rooms_bp.route('/<int:room_id>', methods=['GET'])
@token_required
def get_room_detail(user_id, room_id):
    r = Room.query.get(room_id)
    if not r:
        return jsonify({"success": False, "message": "Room not found"}), 404
    wishlisted_ids = {w.room_id for w in Wishlist.query.filter_by(user_id=user_id).all()}
    return jsonify(room_to_dict(r, wishlisted_ids))

@rooms_bp.route('/wishlist', methods=['GET'])
@token_required
def get_wishlist(user_id):
    wishlisted = Wishlist.query.filter_by(user_id=user_id).all()
    room_ids = [w.room_id for w in wishlisted]
    rooms = Room.query.filter(Room.id.in_(room_ids)).all() if room_ids else []
    return jsonify({"success": True, "rooms": [room_to_dict(r, set(room_ids)) for r in rooms]})

@rooms_bp.route('/wishlist', methods=['POST'])
@token_required
def toggle_wishlist(user_id):
    data = request.json
    room_id = data.get('room_id')
    action = data.get('action')
    existing = Wishlist.query.filter_by(user_id=user_id, room_id=room_id).first()
    if action == "remove":
        if existing:
            db.session.delete(existing)
            db.session.commit()
        return jsonify({"success": True, "message": "Removed from wishlist"})
    else:
        if not existing:
            db.session.add(Wishlist(user_id=user_id, room_id=room_id))
            db.session.commit()
        return jsonify({"success": True, "message": "Added to wishlist"})
        
@rooms_bp.route('/<int:room_id>/rate', methods=['POST'])
@token_required
def rate_room(user_id, room_id):
    data = request.json or {}
    rating_val = data.get('rating')
    
    if rating_val is None:
        return jsonify({"success": False, "message": "Rating value is required"}), 400
        
    rating_val = float(rating_val)
    if rating_val < 0 or rating_val > 5:
        return jsonify({"success": False, "message": "Rating must be between 0 and 5"}), 400
        
    existing = RoomRating.query.filter_by(user_id=user_id, room_id=room_id).first()
    if existing:
        existing.rating = rating_val
    else:
        new_rating = RoomRating(user_id=user_id, room_id=room_id, rating=rating_val)
        db.session.add(new_rating)
        
    db.session.commit()
    return jsonify({"success": True, "message": "Rating applied successfully"})

