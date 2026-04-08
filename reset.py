"""
Run this script to completely reset your StayMatch database.
It will:
  1. Drop all old tables
  2. Re-create them with the correct schema (including is_deleted_a, is_deleted_b, etc.)
  3. Seed fresh demo users with plain-text passwords
"""
from app import create_app
from extensions import db
from seed import seed_database
import pymysql

# First make sure the database exists in MySQL
try:
    conn = pymysql.connect(host='localhost', user='root', password='')
    conn.cursor().execute('CREATE DATABASE IF NOT EXISTS staymatch;')
    conn.close()
    print("✅ Database 'staymatch' exists.")
except Exception as e:
    print(f"⚠️  Could not auto-create database (is XAMPP MySQL running?): {e}")

app = create_app()
with app.app_context():
    print("🗑️  Dropping all old tables...")
    db.drop_all()
    print("🏗️  Creating all tables with correct schema...")
    db.create_all()
    print("🌱  Seeding demo data with plain-text passwords...")
    seed_database()
    print()
    print("✅ Done! Your database is fresh and perfect.")
    print("   You can now login with:")
    print("   Email: priya@example.com | Password: password123")
    print("   Email: jordan@example.com | Password: password123")
    print("   Email: sarah@example.com | Password: password123")
    print("   Email: marcus@example.com | Password: password123")
