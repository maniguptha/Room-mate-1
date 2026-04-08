from extensions import db
from models import Room, User

def seed_database():
    # Check if demo users exist
    if User.query.filter_by(email='barani25043@gmail.com').first():
        print("Demo users already exist. Skipping seed.")
        return

    print("Seeding database with plain-text demo data...")

    # Using plain text password as requested
    pw = 'password123'
    
    u1 = User(name='Priya Sharma', email='priya@example.com', password=pw, location='SoMa, SF', age=24, budget='₹18,000/mo', traits='Early Bird,Clean,WFH', bio='Looking for a shared flat in SoMa.', onboarding_complete=True)
    u2 = User(name='Jordan Mike', email='jordan@example.com', password=pw, location='Mission District', age=26, budget='₹22,000/mo', traits='Night Owl,Social,Gym', bio='Techie looking for a modern loft.', onboarding_complete=True)
    u3 = User(name='Sarah Long', email='sarah@example.com', password=pw, location='Hayes Valley', age=23, budget='₹20,000/mo', traits='Quiet,Pet Friendly,Reader', bio='Peaceful vibes only.', onboarding_complete=True)
    u4 = User(name='Marcus Tan', email='marcus@example.com', password=pw, location='Sunset District', age=28, budget='₹12,000/mo', traits='Student,Gamer,Night Owl', bio='Budget student living.', onboarding_complete=True)

    db.session.add_all([u1, u2, u3, u4])
    db.session.commit()

    # Create Rooms linked to these Users
    db.session.add_all([
        Room(posted_by=u1.id, title='Sunny Studio in SoMa', location='SoMa, San Francisco', price='₹18,000', score=9.4, gradient_color='amber', description='Beautiful naturally lit studio near tech hubs.', amenities='WiFi,Laundry,Gym'),
        Room(posted_by=u2.id, title='Modern Loft', location='Mission District', price='₹24,000', score=8.8, gradient_color='purple', description='Spacious loft with high ceilings.', amenities='WiFi,AC,Parking'),
        Room(posted_by=u3.id, title='Cozy Private Room', location='Hayes Valley', price='₹16,000', score=9.1, gradient_color='blue', description='Quiet room in a 3BHK flat.', amenities='WiFi,Kitchen,Balcony'),
        Room(posted_by=u4.id, title='Shared Apartment', location='Sunset District', price='₹12,000', score=7.5, gradient_color='green', description='Budget friendly shared space.', amenities='WiFi,Kitchen'),
    ])

    db.session.commit()
    print("Database seeded successfully with plain-text passwords!")
