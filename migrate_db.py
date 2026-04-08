from app import create_app
from extensions import db

app = create_app()

with app.app_context():
    # Try creating all tables (will create room_rating)
    db.create_all()

    # Try altering user table directly with raw SQL
    from sqlalchemy import text
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN reset_otp VARCHAR(10);"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Could not add reset_otp (maybe it already exists)", e)
    
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN reset_otp_expiry DATETIME;"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Could not add reset_otp_expiry (maybe it already exists)", e)

    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN latitude FLOAT DEFAULT 0.0;"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Could not add latitude (maybe it already exists)", e)

    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN longitude FLOAT DEFAULT 0.0;"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Could not add longitude (maybe it already exists)", e)

print("Migration completed successfully.")
