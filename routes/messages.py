from flask import Blueprint, request, jsonify
from extensions import db
from models import Conversation, Message, User, BlockedUser
from routes.matches import token_required
import datetime
import os
import uuid

messages_bp = Blueprint('messages', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
UPLOAD_CHAT   = os.path.join(UPLOAD_FOLDER, 'chat')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_CHAT,   exist_ok=True)

def _now():
    return datetime.datetime.now().strftime("%I:%M %p")

def _convo_for_user(c, user_id):
    """Serialize a conversation from the perspective of a specific user."""
    is_a = (c.user_a_id == user_id)
    return {
        "id": c.id,
        "name": c.name_for_a if is_a else c.name_for_b,
        "last_message": c.last_message or "",
        "time": c.last_message_time or "",
        "unread": c.unread_a if is_a else c.unread_b,
        "avatar_color": c.avatar_color or "violet",
        "is_ai": False,
        "other_user_id": c.user_b_id if is_a else c.user_a_id
    }

# ─── GET conversations for the logged-in user ────────────────────────────────
@messages_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations(user_id):
    convos = Conversation.query.filter(
        db.or_(
            db.and_(Conversation.user_a_id == user_id, Conversation.is_deleted_a == False),
            db.and_(Conversation.user_b_id == user_id, Conversation.is_deleted_b == False)
        )
    ).order_by(Conversation.id.desc()).all()

    return jsonify({
        "success": True,
        "conversations": [_convo_for_user(c, user_id) for c in convos]
    })

# ─── POST create a conversation (or return existing) ─────────────────────────
@messages_bp.route('/conversations', methods=['POST'])
@token_required
def create_conversation(user_id):
    data = request.json
    other_user_id = data.get('other_user_id')   # ID of the person being contacted
    name = data.get('name', 'Chat')             # display name from sender's perspective
    avatar_color = data.get('avatar_color', 'violet')

    # Prevent user from messaging themselves
    if user_id == other_user_id:
        return jsonify({"success": False, "message": "You cannot message yourself"}), 400

    # Ensure the other user exists
    other_user = User.query.get(other_user_id)
    if not other_user:
        return jsonify({"success": False, "message": "User does not exist"}), 404

    # Check for blocking
    if BlockedUser.query.filter_by(blocker_id=other_user_id, blocked_id=user_id).first():
        return jsonify({"success": False, "message": "You are blocked by this user"}), 403
    if BlockedUser.query.filter_by(blocker_id=user_id, blocked_id=other_user_id).first():
        return jsonify({"success": False, "message": "You have blocked this user"}), 403

    # Look up existing conversation between these two users
    existing = Conversation.query.filter(
        db.or_(
            db.and_(Conversation.user_a_id == user_id,  Conversation.user_b_id == other_user_id),
            db.and_(Conversation.user_a_id == other_user_id, Conversation.user_b_id == user_id)
        )
    ).first()

    if existing:
        return jsonify({"success": True, "id": existing.id})

    # Get current user's name so other side sees it
    me = User.query.get(user_id)
    my_name = me.name if me else "User"

    new_convo = Conversation(
        user_a_id=user_id,
        user_b_id=other_user_id,
        name_for_a=name,           # sender sees the recipient's name
        name_for_b=my_name,        # recipient sees the sender's name
        last_message="",
        last_message_time=_now(),
        unread_a=0,
        unread_b=0,
        avatar_color=avatar_color
    )
    db.session.add(new_convo)
    db.session.commit()
    return jsonify({"success": True, "id": new_convo.id}), 201

@messages_bp.route('/conversations/<int:convo_id>', methods=['DELETE'])
@token_required
def delete_conversation(user_id, convo_id):
    convo = Conversation.query.get(convo_id)
    if not convo or user_id not in (convo.user_a_id, convo.user_b_id):
        return jsonify({"success": False, "message": "Forbidden"}), 403
        
    if convo.user_a_id == user_id:
        convo.is_deleted_a = True
    else:
        convo.is_deleted_b = True
        
    db.session.commit()
    return jsonify({"success": True, "message": "Chat deleted"})

# ─── GET messages in a conversation ──────────────────────────────────────────
@messages_bp.route('/conversations/<int:convo_id>/messages', methods=['GET'])
@token_required
def get_messages(user_id, convo_id):
    convo = Conversation.query.get(convo_id)
    if not convo:
        return jsonify({"success": False, "message": "Conversation not found"}), 404

    # Permission check: only participants can read
    if user_id not in (convo.user_a_id, convo.user_b_id):
        return jsonify({"success": False, "message": "Forbidden"}), 403

    # Mark as read for the calling user
    if convo.user_a_id == user_id and convo.unread_a > 0:
        convo.unread_a = 0
        db.session.commit()
    elif convo.user_b_id == user_id and convo.unread_b > 0:
        convo.unread_b = 0
        db.session.commit()

    msgs = Message.query.filter_by(conversation_id=convo_id).order_by(Message.created_at.asc()).all()
    filtered_msgs = []
    
    is_a = (convo.user_a_id == user_id)
    
    for m in msgs:
        if m.is_deleted_everyone:
            continue
        if is_a and m.is_deleted_for_a:
            continue
        if not is_a and m.is_deleted_for_b:
            continue
            
        reply_data = None
        if m.reply_to_id:
            orig = Message.query.get(m.reply_to_id)
            if orig:
                # Check who sent the original to show "You" or Name
                orig_sender = User.query.get(orig.sender_id)
                reply_data = {
                    "id": orig.id,
                    "text": orig.text or "",
                    "media_type": orig.media_type or "",
                    "sender_name": "You" if orig.sender_id == user_id else (orig_sender.name if orig_sender else "User")
                }
            
        filtered_msgs.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "role": "user" if m.sender_id == user_id else "other",
            "text": m.text or "",
            "media_url": m.media_url or "",
            "media_type": m.media_type or "",
            "time": m.time,
            "reply_to_id": m.reply_to_id,
            "reply_data": reply_data
        })

    return jsonify({
        "success": True,
        "my_user_id": user_id,
        "messages": filtered_msgs
    })

# ─── POST send a text message ─────────────────────────────────────────────────
@messages_bp.route('/conversations/<int:convo_id>/messages', methods=['POST'])
@token_required
def send_message(user_id, convo_id):
    convo = Conversation.query.get(convo_id)
    if not convo:
        return jsonify({"success": False, "message": "Conversation not found"}), 404
    if user_id not in (convo.user_a_id, convo.user_b_id):
        return jsonify({"success": False, "message": "Forbidden"}), 403

    # Check for blocking before sending
    other_id = convo.user_b_id if convo.user_a_id == user_id else convo.user_a_id
    if BlockedUser.query.filter_by(blocker_id=other_id, blocked_id=user_id).first():
        return jsonify({"success": False, "message": "You are blocked by this user"}), 403
    if BlockedUser.query.filter_by(blocker_id=user_id, blocked_id=other_id).first():
        return jsonify({"success": False, "message": "You have blocked this user"}), 403

    data = request.json
    text = (data.get('message') or '').strip()
    if not text:
        return jsonify({"success": False, "message": "Message cannot be empty"}), 400

    now = _now()
    new_msg = Message(
        conversation_id=convo_id,
        sender_id=user_id,
        text=text,
        time=now,
        reply_to_id=data.get('reply_to_id')
    )
    db.session.add(new_msg)

    # Update conversation preview + increment recipient's unread
    convo.last_message = text[:255]
    convo.last_message_time = now
    if convo.user_a_id == user_id:
        convo.unread_b = (convo.unread_b or 0) + 1
    else:
        convo.unread_a = (convo.unread_a or 0) + 1

    db.session.commit()

    reply_data = None
    if new_msg.reply_to_id:
        orig = Message.query.get(new_msg.reply_to_id)
        if orig:
            orig_sender = User.query.get(orig.sender_id)
            reply_data = {
                "id": orig.id,
                "text": orig.text or "",
                "media_type": orig.media_type or "",
                "sender_name": "You" if orig.sender_id == user_id else (orig_sender.name if orig_sender else "User")
            }

    return jsonify({
        "id": new_msg.id,
        "sender_id": user_id,
        "role": "user",
        "text": text,
        "media_url": "",
        "media_type": "",
        "time": now,
        "reply_to_id": new_msg.reply_to_id,
        "reply_data": reply_data
    }), 201

# ─── POST upload media (image/video) ─────────────────────────────────────────
@messages_bp.route('/conversations/<int:convo_id>/media', methods=['POST'])
@token_required
def send_media(user_id, convo_id):
    convo = Conversation.query.get(convo_id)
    if not convo or user_id not in (convo.user_a_id, convo.user_b_id):
        return jsonify({"success": False, "message": "Forbidden"}), 403

    # Check for blocking before sending media
    other_id = convo.user_b_id if convo.user_a_id == user_id else convo.user_a_id
    if BlockedUser.query.filter_by(blocker_id=other_id, blocked_id=user_id).first():
        return jsonify({"success": False, "message": "You are blocked by this user"}), 403
    if BlockedUser.query.filter_by(blocker_id=user_id, blocked_id=other_id).first():
        return jsonify({"success": False, "message": "You have blocked this user"}), 403

    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400

    file = request.files['file']
    ext = os.path.splitext(file.filename)[1].lower()
    allowed_images = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    allowed_videos = {'.mp4', '.mov', '.avi', '.mkv'}

    if ext in allowed_images:
        media_type = 'image'
    elif ext in allowed_videos:
        media_type = 'video'
    else:
        return jsonify({"success": False, "message": "Unsupported file type"}), 400

    filename = f"chat_{convo_id}_{user_id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_CHAT, filename)
    file.save(filepath)
    media_url = f"/uploads/chat/{filename}"

    now = _now()
    new_msg = Message(
        conversation_id=convo_id,
        sender_id=user_id,
        text="",
        media_url=media_url,
        media_type=media_type,
        time=now
    )
    db.session.add(new_msg)

    preview = "📷 Photo" if media_type == 'image' else "🎥 Video"
    convo.last_message = preview
    convo.last_message_time = now
    if convo.user_a_id == user_id:
        convo.unread_b = (convo.unread_b or 0) + 1
    else:
        convo.unread_a = (convo.unread_a or 0) + 1

    db.session.commit()

    return jsonify({
        "id": new_msg.id,
        "sender_id": user_id,
        "role": "user",
        "text": "",
        "media_url": media_url,
        "media_type": media_type,
        "time": now
    }), 201

# ─── GET unread count (for badge on Messages tab) ───────────────────────────
@messages_bp.route('/unread', methods=['GET'])
@token_required
def get_unread_count(user_id):
    a_unread = db.session.query(db.func.sum(Conversation.unread_a)).filter(
        Conversation.user_a_id == user_id).scalar() or 0
    b_unread = db.session.query(db.func.sum(Conversation.unread_b)).filter(
        Conversation.user_b_id == user_id).scalar() or 0
    return jsonify({"success": True, "unread": a_unread + b_unread})

@messages_bp.route('/conversations/<int:convo_id>/messages/<int:msg_id>', methods=['DELETE'])
@token_required
def delete_message(user_id, convo_id, msg_id):
    convo = Conversation.query.get(convo_id)
    if not convo or user_id not in (convo.user_a_id, convo.user_b_id):
        return jsonify({"success": False, "message": "Forbidden"}), 403

    msg = Message.query.get(msg_id)
    if not msg or msg.conversation_id != convo_id:
        return jsonify({"success": False, "message": "Message not found"}), 404

    # Are they requesting delete for everyone?
    everyone = request.args.get('everyone', 'false').lower() == 'true'

    if everyone:
        # Only the sender can delete for everyone
        if msg.sender_id != user_id:
            return jsonify({"success": False, "message": "Cannot delete others' messages for everyone"}), 400
        msg.is_deleted_everyone = True
    else:
        # Delete for just this user
        if convo.user_a_id == user_id:
            msg.is_deleted_for_a = True
        else:
            msg.is_deleted_for_b = True

    db.session.commit()
    return jsonify({"success": True, "message": "Message deleted"})

@messages_bp.route('/block/<int:target_id>', methods=['POST'])
@token_required
def block_user(user_id, target_id):
    if user_id == target_id:
        return jsonify({"success": False, "message": "Cannot block yourself"}), 400
    if BlockedUser.query.filter_by(blocker_id=user_id, blocked_id=target_id).first():
        return jsonify({"success": True, "message": "User already blocked"})
    
    new_block = BlockedUser(blocker_id=user_id, blocked_id=target_id)
    db.session.add(new_block)
    db.session.commit()
    return jsonify({"success": True, "message": "User blocked"})

@messages_bp.route('/unblock/<int:target_id>', methods=['POST'])
@token_required
def unblock_user(user_id, target_id):
    block = BlockedUser.query.filter_by(blocker_id=user_id, blocked_id=target_id).first()
    if block:
        db.session.delete(block)
        db.session.commit()
    return jsonify({"success": True, "message": "User unblocked"})
