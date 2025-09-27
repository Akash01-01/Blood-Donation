#!/usr/bin/env python3
"""
Add a test blood request to verify filtering works
"""

import sqlite3
from datetime import datetime, timedelta

def add_test_request():
    """Add a test blood request"""
    try:
        conn = sqlite3.connect('instance/blood_finder.db')
        cursor = conn.cursor()
        
        # Add a new test request
        needed_date = (datetime.now() + timedelta(days=3)).isoformat()
        request_date = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO blood_request (
                receiver_id, blood_group_needed, quantity_needed, urgency,
                hospital_name, hospital_location, contact_person, contact_number,
                needed_by_date, additional_notes, request_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            3,  # jack's receiver ID
            'A+',  # Compatible with akash's O+ blood
            '2 units (450ml)',
            'High',
            'Test Hospital',
            'Test Location',
            'Test Person',
            '1234567890',
            needed_date,
            'Test request to verify filtering works',
            request_date,
            'Active'
        ))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Created new test request with ID: {request_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    add_test_request()