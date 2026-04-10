from flask import Flask, send_from_directory
from flask_cors import CORS
from extensions import db
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Disable strict slashes so /api/matches works the same as /api/matches/
    app.url_map.strict_slashes = False

    @app.route('/')
    def index():
        return "<h2>🚀 StayMatch API is running successfully!</h2><p>Access the endpoints at <code>/api/...</code></p>"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ── Production-safe config ──────────────────────────────────────────────
    # Set DATABASE_URL and SECRET_KEY as environment variables on your server.
    # Fallback to local XAMPP values for local development only.
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY', 'super-secret-staymatch-key-123'
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/staymatch'   # local fallback
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max upload
    # ────────────────────────────────────────────────────────────────────────

    # Serve uploaded media (images/videos) – including sub-directories like /uploads/rooms/
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(UPLOAD_DIR, filename)

    db.init_app(app)

    from routes.auth import auth_bp
    from routes.onboarding import onboarding_bp
    from routes.profile import profile_bp
    from routes.matches import matches_bp
    from routes.rooms import rooms_bp
    from routes.messages import messages_bp
    from routes.ai_score import ai_score_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(onboarding_bp, url_prefix='/api/onboarding')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(matches_bp, url_prefix='/api/matches')
    app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(ai_score_bp, url_prefix='/api/rooms')

    return app


# ── Expose app at module level so gunicorn can find it ─────────────────────
# On your server run:  gunicorn app:app
app = create_app()

with app.app_context():
    db.create_all()
    from seed import seed_database
    seed_database()


if __name__ == '__main__':
    # Local development only — auto-create MySQL DB via XAMPP
    import pymysql
    try:
        conn = pymysql.connect(host='localhost', user='root', password='')
        conn.cursor().execute('CREATE DATABASE IF NOT EXISTS staymatch;')
        conn.close()
    except Exception as e:
        print("Could not auto-create database (make sure XAMPP MySQL is running!):", e)

    print("StayMatch Backend running at http://127.0.0.1:5000")
    # debug=False is safe for production; True only for local dev
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true',
            host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
