import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('instance/blood_finder.db')
cursor = conn.cursor()

print("=== CURRENT SYSTEM STATUS ===")

# Check all users
print("\n1. ALL DONORS:")
cursor.execute("SELECT id, name, blood_group, availability, location FROM donor")
donors = cursor.fetchall()
for donor in donors:
    print(f"   ID {donor[0]}: {donor[1]} ({donor[2]}) - Available: {donor[3]} - Location: {donor[4]}")

print("\n2. ALL RECEIVERS:")
cursor.execute("SELECT id, name, location FROM receiver")
receivers = cursor.fetchall()
for receiver in receivers:
    print(f"   ID {receiver[0]}: {receiver[1]} - Location: {receiver[2]}")

print("\n3. ACTIVE BLOOD REQUESTS:")
cursor.execute("SELECT id, receiver_id, blood_group_needed, contact_person, hospital_location, status, requesting_for, patient_name FROM blood_request WHERE status = 'Active'")
requests = cursor.fetchall()
for req in requests:
    print(f"   Request ID {req[0]}: {req[2]} blood for {req[3]} at {req[4]}")
    print(f"      Status: {req[5]}, Requesting for: {req[6]}")
    if req[7]:
        print(f"      Patient: {req[7]}")

print("\n4. DONATION RESPONSES:")
cursor.execute("SELECT id, request_id, donor_id, status FROM donation_response")
responses = cursor.fetchall()
for resp in responses:
    print(f"   Response ID {resp[0]}: Donor {resp[2]} -> Request {resp[1]} ({resp[3]})")

print("\n=== COMPATIBILITY TEST ===")
print("\n5. BLOOD COMPATIBILITY CHECK:")
print("   O+ donors should be able to donate to: O+, A+, B+, AB+")
print("   B+ donors should be able to donate to: B+, AB+")

# Test blood compatibility
cursor.execute("SELECT id, blood_group_needed, contact_person FROM blood_request WHERE status = 'Active'")
active_requests = cursor.fetchall()

cursor.execute("SELECT id, name, blood_group FROM donor WHERE availability = 1")
available_donors = cursor.fetchall()

print(f"\n6. MATCHING TEST:")
for request in active_requests:
    req_id, blood_needed, contact = request
    print(f"   Request: {blood_needed} blood for {contact}")
    
    compatible_donors = []
    for donor in available_donors:
        donor_id, donor_name, donor_blood = donor
        
        # Apply compatibility rules
        can_donate = False
        if donor_blood == blood_needed:
            can_donate = True
        elif donor_blood == 'O-':
            can_donate = True  # Universal donor
        elif donor_blood == 'O+' and blood_needed in ['O+', 'A+', 'B+', 'AB+']:
            can_donate = True
        elif donor_blood == 'A-' and blood_needed in ['A-', 'A+', 'AB-', 'AB+']:
            can_donate = True
        elif donor_blood == 'A+' and blood_needed in ['A+', 'AB+']:
            can_donate = True
        elif donor_blood == 'B-' and blood_needed in ['B-', 'B+', 'AB-', 'AB+']:
            can_donate = True
        elif donor_blood == 'B+' and blood_needed in ['B+', 'AB+']:
            can_donate = True
        elif donor_blood == 'AB-' and blood_needed in ['AB-', 'AB+']:
            can_donate = True
        elif donor_blood == 'AB+' and blood_needed == 'AB+':
            can_donate = True
            
        if can_donate:
            compatible_donors.append(f"{donor_name} ({donor_blood})")
    
    if compatible_donors:
        print(f"      Compatible donors: {', '.join(compatible_donors)}")
    else:
        print(f"      No compatible donors found")

conn.close()
print("\n=== TEST COMPLETE ===")