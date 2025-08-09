from app import db, app

# Create database and tables
with app.app_context():
    db.create_all()
    print("Database 'blood_finder.db' created successfully!")
    print("Tables created: User, Donor, Receiver")
