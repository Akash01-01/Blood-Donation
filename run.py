import subprocess
import sys
import os

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Step 1: Initialize database only if it doesn't exist
db_path = 'instance/blood_finder.db'
if not os.path.exists(db_path):
    print("Creating new database...")
    try:
        subprocess.run([sys.executable, "create_db.py"], check=True)
        print("Database created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error creating database: {e}")
        sys.exit(1)
else:
    print("Database already exists, skipping creation...")

# Step 2: Start the Flask app
print("\n" + "="*50)
print("🩸 BLOOD DONATION MANAGEMENT SYSTEM 🩸")
print("="*50)
print("Starting Flask development server...")
print("The app will be available at: http://127.0.0.1:5000")
print("Press Ctrl+C to stop the server")
print("="*50 + "\n")

try:
    subprocess.run([sys.executable, "app.py"])
except KeyboardInterrupt:
    print("\n" + "="*50)
    print("Server stopped by user (Ctrl+C)")
    print("Thank you for using the Blood Donation Management System!")
    print("="*50)
except Exception as e:
    print(f"\nError starting the Flask app: {e}")
    sys.exit(1)
