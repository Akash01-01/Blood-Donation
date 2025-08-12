from app import db, app, Admin
from werkzeug.security import generate_password_hash
import os

# Delete the existing database file completely
db_path = 'instance/blood_finder.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("Old database file deleted")

# Create database and tables from scratch
with app.app_context():
    # Create new tables (this will only create Donor, Receiver, Admin)
    db.create_all()
    
    # Create default admin
    admin = Admin(
        name='Administrator',
        email='admin@bloodfinder.com',
        password=generate_password_hash('admin123')
    )
    db.session.add(admin)
    db.session.commit()
    
    print("New database created successfully!")
    print("Tables created: Donor, Receiver, Admin")
    print("Default admin created:")
    print("Email: admin@bloodfinder.com")
    print("Password: admin123")
