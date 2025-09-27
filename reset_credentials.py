from app import app, db, Donor, Receiver, BloodRequest, DonationResponse, DonationHistory
from werkzeug.security import generate_password_hash

def reset_to_original_credentials():
    """Reset all passwords back to 12345 and remove test users"""
    with app.app_context():
        print("🔧 Resetting database to original state...")
        print("=" * 50)
        
        # Remove test users (keep only original akash and jack)
        test_emails = [
            'donor1@test.com', 'donor2@test.com', 'donor3@test.com',
            'patient1@test.com', 'patient2@test.com'
        ]
        
        # Remove test donors
        for email in test_emails:
            donor = Donor.query.filter_by(email=email).first()
            if donor:
                # Remove their responses first
                DonationResponse.query.filter_by(donor_id=donor.id).delete()
                DonationHistory.query.filter_by(donor_id=donor.id).delete()
                db.session.delete(donor)
                print(f"❌ Removed test donor: {email}")
        
        # Remove test receivers
        for email in test_emails:
            receiver = Receiver.query.filter_by(email=email).first()
            if receiver:
                # Remove their requests first
                requests = BloodRequest.query.filter_by(receiver_id=receiver.id).all()
                for request in requests:
                    DonationResponse.query.filter_by(request_id=request.id).delete()
                    db.session.delete(request)
                db.session.delete(receiver)
                print(f"❌ Removed test receiver: {email}")
        
        # Reset original users passwords to 12345
        original_password = generate_password_hash('12345')
        
        # Update Akash
        akash = Donor.query.filter_by(email='akash@gmail.com').first()
        if akash:
            akash.password = original_password
            print(f"✅ Reset Akash password to: 12345")
        
        # Update Jack 
        jack = Receiver.query.filter_by(email='jack@gmail.com').first()
        if jack:
            jack.password = original_password
            print(f"✅ Reset Jack password to: 12345")
        
        # Update any other original users
        rakhi = Donor.query.filter_by(email='rakhi@gmail.com').first()
        if rakhi:
            rakhi.password = original_password
            print(f"✅ Reset Rakhi password to: 12345")
        
        db.session.commit()
        
        print("\n📊 Current Users After Cleanup:")
        print("-" * 30)
        
        donors = Donor.query.all()
        for donor in donors:
            print(f"👤 Donor: {donor.name} ({donor.email}) - {donor.blood_group}")
        
        receivers = Receiver.query.all()  
        for receiver in receivers:
            print(f"🏥 Receiver: {receiver.name} ({receiver.email})")
        
        print(f"\n🔑 All passwords reset to: 12345")
        print(f"✅ System is now clean and ready for all users!")

if __name__ == "__main__":
    reset_to_original_credentials()