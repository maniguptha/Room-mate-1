from extensions import db
import datetime

class BlockedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    bio = db.Column(db.Text)
    budget = db.Column(db.String(50))
    age = db.Column(db.Integer)
    traits = db.Column(db.Text)
    onboarding_complete = db.Column(db.Boolean, default=False)
    # FCM push token for delivery notifications
    fcm_token = db.Column(db.String(255))
    profile_pic = db.Column(db.String(500))
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    reset_otp = db.Column(db.String(10))
    reset_otp_expiry = db.Column(db.DateTime)

class QuizAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sleep_schedule = db.Column(db.String(50))
    cleanliness = db.Column(db.String(50))
    noise_level = db.Column(db.String(50))
    guests = db.Column(db.String(50))
    budget_max = db.Column(db.Integer)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # who posted it
    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float)          # overall AI score (0-10)
    gradient_color = db.Column(db.String(50))
    description = db.Column(db.Text)
    amenities = db.Column(db.String(500))
    photos = db.Column(db.Text)          # JSON list of uploaded photo filenames
    # AI analysis sub-scores (0-100)
    ai_score = db.Column(db.Float, default=0.0)       # overall 0-100
    ai_hygiene = db.Column(db.Integer, default=0)
    ai_safety = db.Column(db.Integer, default=0)
    ai_lifestyle = db.Column(db.Integer, default=0)
    ai_feedback = db.Column(db.Text)      # AI-generated textual feedback
    room_type = db.Column(db.String(50))
    furnishing = db.Column(db.String(50))
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)

# Roommate table is now redundant as we use User table for everyone.
# Removed Roommate table definition.

class RoomRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class CompatibilityScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    score = db.Column(db.Integer)

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', ondelete="CASCADE"))

class Conversation(db.Model):
    """
    A conversation is owned by exactly TWO participants (user_a and user_b).
    Each participant sees their own unread count.
    Only these two users can see this conversation.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_a_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user_b_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    # Display name from each participant's perspective
    name_for_a = db.Column(db.String(100))   # what user_a sees as the chat name
    name_for_b = db.Column(db.String(100))   # what user_b sees as the chat name
    last_message = db.Column(db.String(255))
    last_message_time = db.Column(db.String(50))
    unread_a = db.Column(db.Integer, default=0)  # unread count for user_a
    unread_b = db.Column(db.Integer, default=0)  # unread count for user_b
    avatar_color = db.Column(db.String(50), default='violet')
    is_deleted_a = db.Column(db.Boolean, default=False)
    is_deleted_b = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Message(db.Model):
    """
    A message in a conversation. sender_id identifies who sent it.
    media_url stores the path if a photo/video was sent.
    """
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id', ondelete="CASCADE"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    text = db.Column(db.Text)
    media_url = db.Column(db.String(500))  # for images/videos
    media_type = db.Column(db.String(20))  # 'image' or 'video'
    time = db.Column(db.String(50))
    reply_to_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    is_deleted_for_a = db.Column(db.Boolean, default=False)
    is_deleted_for_b = db.Column(db.Boolean, default=False)
    is_deleted_everyone = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
