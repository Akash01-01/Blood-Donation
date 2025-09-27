import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('instance/blood_finder.db')
cursor = conn.cursor()

print("Adding new columns to blood_request table...")

try:
    # Add the new columns to the existing table
    cursor.execute('ALTER TABLE blood_request ADD COLUMN requesting_for TEXT DEFAULT "myself"')
    cursor.execute('ALTER TABLE blood_request ADD COLUMN patient_name TEXT')
    cursor.execute('ALTER TABLE blood_request ADD COLUMN patient_relation TEXT')
    
    # Update existing records to have requesting_for = 'myself'
    cursor.execute('UPDATE blood_request SET requesting_for = "myself" WHERE requesting_for IS NULL')
    
    conn.commit()
    print("✅ Successfully added new columns!")
    print("✅ Updated existing records to 'myself'")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ Columns already exist, no migration needed.")
    else:
        print(f"❌ Error: {e}")

# Show the updated table structure
print("\n=== Updated Table Structure ===")
cursor.execute("PRAGMA table_info(blood_request)")
columns = cursor.fetchall()
for col in columns:
    print(f"- {col[1]} ({col[2]})")

conn.close()
print("\nDatabase migration completed!")