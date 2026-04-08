from flask import Blueprint, request, jsonify
from extensions import db
from models import User, QuizAnswer
import jwt

onboarding_bp = Blueprint('onboarding', __name__)
SECRET_KEY = 'super-secret-staymatch-key-123'

def token_required(f):
    def decorator(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator

@onboarding_bp.route('/', methods=['POST'])
@token_required
def submit_onboarding(current_user):
    data = request.json
    answers = data.get('answers', [])
    quiz = QuizAnswer.query.filter_by(user_id=current_user.id).first()
    if not quiz:
        quiz = QuizAnswer(user_id=current_user.id)
        db.session.add(quiz)
    for ans in answers:
        q = ans.get('question', '').lower()
        a = ans.get('answer', '')
        if 'sleep' in q: quiz.sleep_schedule = a
        if 'clean' in q: quiz.cleanliness = a
        if 'noise' in q: quiz.noise_level = a
        if 'guests' in q: quiz.guests = a
        if 'budget' in q:
            digits = "".join(filter(str.isdigit, a.split('–')[0]))
            quiz.budget_max = int(digits) if digits else 0
    current_user.onboarding_complete = True
    db.session.commit()
    return jsonify({"success": True, "message": "Onboarding completed successfully"})
