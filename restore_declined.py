#!/usr/bin/env python3
"""
Re-add declined responses to keep requests filtered out
"""

import sqlite3
from datetime import datetime

def add_declined_responses():
    """Add declined responses for requests 3, 4, 5, 6"""
    try:
        conn = sqlite3.connect('instance/blood_finder.db')
        cursor = conn.cursor()
        
        # Add declined responses for donor 1 (akash)
        declined_requests = [3, 4, 5, 6]  # The requests you declined
        response_date = datetime.now().isoformat()
        
        for request_id in declined_requests:
            cursor.execute("""
                INSERT OR IGNORE INTO donation_response (
                    request_id, donor_id, status, donor_notes, response_date
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                request_id,
                1,  # akash's donor ID
                'Rejected',
                'Previously declined by user',
                response_date
            ))
        
        conn.commit()
        added_count = cursor.rowcount
        conn.close()
        
        print(f"✅ Re-added {len(declined_requests)} declined responses")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    add_declined_responses()