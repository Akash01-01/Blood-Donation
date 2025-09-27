from app import app, db, Donor, Receiver

with app.app_context():
    print("=== ALL DONORS ===")
    donors = Donor.query.all()
    for donor in donors:
        print(f"ID: {donor.id}")
        print(f"Name: {donor.name}")
        print(f"Email: {donor.email}")
        print(f"Location: '{donor.location}'")
        print(f"Blood Group: {donor.blood_group}")
        print(f"Available: {donor.availability}")
        print(f"Contact: {donor.contact}")
        print("-" * 40)
    
    print("\n=== ALL RECEIVERS ===")
    receivers = Receiver.query.all()
    for receiver in receivers:
        print(f"ID: {receiver.id}")
        print(f"Name: {receiver.name}")
        print(f"Email: {receiver.email}")
        print(f"Location: '{receiver.location}'")
        print(f"Contact: {receiver.contact}")
        print("-" * 40)