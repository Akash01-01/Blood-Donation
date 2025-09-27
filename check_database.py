from app import app, db, Donor, Receiver, Admin, BloodRequest, DonationResponse, DonationHistory

def check_database():
    with app.app_context():
        print("=" * 60)
        print("🩸 BLOOD DONATION DATABASE CONTENTS")
        print("=" * 60)
        
        # Check Donors
        donors = Donor.query.all()
        print(f"\n📋 DONORS ({len(donors)} total):")
        print("-" * 40)
        if donors:
            for donor in donors:
                print(f"ID: {donor.id}")
                print(f"Name: {donor.name}")
                print(f"Email: {donor.email}")
                print(f"Blood Group: {donor.blood_group}")
                print(f"Age: {donor.age}")
                print(f"Gender: {donor.gender}")
                print(f"Location: {donor.location}")
                print(f"Contact: {donor.contact}")
                print(f"Available: {'Yes' if donor.availability else 'No'}")
                print(f"Geocoded: {'Yes' if donor.geocoded else 'No'}")
                if donor.latitude and donor.longitude:
                    print(f"Coordinates: {donor.latitude}, {donor.longitude}")
                print("-" * 40)
        else:
            print("No donors found in database.")
        
        # Check Receivers
        receivers = Receiver.query.all()
        print(f"\n📋 RECEIVERS ({len(receivers)} total):")
        print("-" * 40)
        if receivers:
            for receiver in receivers:
                print(f"ID: {receiver.id}")
                print(f"Name: {receiver.name}")
                print(f"Email: {receiver.email}")
                print(f"Location: {receiver.location}")
                print(f"Contact: {receiver.contact}")
                print(f"Geocoded: {'Yes' if receiver.geocoded else 'No'}")
                if receiver.latitude and receiver.longitude:
                    print(f"Coordinates: {receiver.latitude}, {receiver.longitude}")
                print("-" * 40)
        else:
            print("No receivers found in database.")
        
        # Check Admins
        admins = Admin.query.all()
        print(f"\n👤 ADMINS ({len(admins)} total):")
        print("-" * 40)
        if admins:
            for admin in admins:
                print(f"ID: {admin.id}")
                print(f"Name: {admin.name}")
                print(f"Email: {admin.email}")
                print("-" * 40)
        else:
            print("No admins found in database.")
        
        # Check Blood Requests
        requests = BloodRequest.query.all()
        print(f"\n🩸 BLOOD REQUESTS ({len(requests)} total):")
        print("-" * 40)
        if requests:
            for request in requests:
                print(f"ID: {request.id}")
                print(f"Receiver: {request.receiver.name}")
                print(f"Blood Group Needed: {request.blood_group_needed}")
                print(f"Quantity: {request.quantity_needed}")
                print(f"Urgency: {request.urgency}")
                print(f"Hospital: {request.hospital_name}")
                print(f"Location: {request.hospital_location}")
                print(f"Status: {request.status}")
                print(f"Created: {request.request_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Needed By: {request.needed_by_date.strftime('%Y-%m-%d')}")
                print("-" * 40)
        else:
            print("No blood requests found in database.")
        
        # Check Donation Responses
        responses = DonationResponse.query.all()
        print(f"\n💬 DONATION RESPONSES ({len(responses)} total):")
        print("-" * 40)
        if responses:
            for response in responses:
                print(f"ID: {response.id}")
                print(f"Donor: {response.donor.name}")
                print(f"Request ID: {response.request_id}")
                print(f"Status: {response.status}")
                print(f"Response Date: {response.response_date.strftime('%Y-%m-%d %H:%M:%S')}")
                if response.donor_notes:
                    print(f"Donor Notes: {response.donor_notes}")
                if response.receiver_notes:
                    print(f"Receiver Notes: {response.receiver_notes}")
                print("-" * 40)
        else:
            print("No donation responses found in database.")
        
        # Check Donation History
        donations = DonationHistory.query.all()
        print(f"\n📊 DONATION HISTORY ({len(donations)} total):")
        print("-" * 40)
        if donations:
            for donation in donations:
                print(f"ID: {donation.id}")
                print(f"Donor: {donation.donor_id}")
                print(f"Blood Type: {donation.blood_type}")
                print(f"Quantity: {donation.quantity}")
                print(f"Date: {donation.donation_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Location: {donation.location}")
                print(f"Status: {donation.status}")
                if donation.notes:
                    print(f"Notes: {donation.notes}")
                print("-" * 40)
        else:
            print("No donation history found in database.")
        
        print("\n" + "=" * 60)
        print("DATABASE CHECK COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    check_database()