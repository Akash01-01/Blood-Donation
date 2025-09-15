import subprocess
import sys
import os

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Step 1: Initialize database only if it doesn't exist
db_path = 'instance/blood_finder.db'
if not os.path.exists(db_path):
    print("Creating new database...")
    subprocess.run([sys.executable, "create_db.py"], check=True)
else:
    print("Database already exists, skipping creation...")

# Step 2: Start the Flask app
print("Starting Flask app...")
subprocess.run([sys.executable, "app.py"])
