from app import db, app, Admin
from werkzeug.security import generate_password_hash

# Create database and tables
with app.app_context():
    # Drop all tables first to avoid conflicts
    db.drop_all()
    
    # Execute raw SQL to ensure User table is completely removed
    try:
        db.engine.execute('DROP TABLE IF EXISTS user')
        print("User table dropped successfully")
    except:
        print("User table already doesn't exist")
    
    # Create new tables
    db.create_all()
    
    # Create default admin
    admin = Admin(
        name='Administrator',
        email='admin@bloodfinder.com',
        password=generate_password_hash('admin123')
    )
    db.session.add(admin)
    db.session.commit()
    
    print("Database 'blood_finder.db' created successfully!")
    print("Tables created: Donor, Receiver, Admin, DonationHistory, BloodRequest, DonationResponse")
    print("Default admin created:")
    print("Email: admin@bloodfinder.com")
    print("Password: admin123")
    print("Enhanced features:")
    print("- Role switching between Donor and Recipient")
    print("- Donation history tracking")
    print("- Blood request management")
    print("- Donation response system")
