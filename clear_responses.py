#!/usr/bin/env python3
"""
Script to manually clear all donation responses for a specific donor
"""

import sqlite3
import sys

def clear_donor_responses(donor_id=1):
    """Clear all donation responses for a specific donor"""
    try:
        # Connect to database
        conn = sqlite3.connect('instance/blood_finder.db')
        cursor = conn.cursor()
        
        # First, show current responses
        cursor.execute('SELECT COUNT(*) FROM donation_response WHERE donor_id = ?', (donor_id,))
        current_count = cursor.fetchone()[0]
        print(f"Current responses for donor {donor_id}: {current_count}")
        
        if current_count == 0:
            print("No responses to delete.")
            return True
        
        # Delete all responses for the donor
        cursor.execute('DELETE FROM donation_response WHERE donor_id = ?', (donor_id,))
        affected = cursor.rowcount
        conn.commit()
        
        print(f"✅ Deleted {affected} responses for donor {donor_id}")
        
        # Show total remaining
        cursor.execute('SELECT COUNT(*) FROM donation_response')
        total_remaining = cursor.fetchone()[0]
        print(f"Total responses remaining in database: {total_remaining}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    donor_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    success = clear_donor_responses(donor_id)
    sys.exit(0 if success else 1)