

import subprocess
import sys
import os

# Always use absolute paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'blood_finder.db')
CREATE_DB_PATH = os.path.join(BASE_DIR, 'create_db.py')
APP_PATH = os.path.join(BASE_DIR, 'app.py')

# Path to the virtual environment's Python
VENV_PYTHON = os.path.abspath(os.path.join(BASE_DIR, '..', '.venv', 'Scripts', 'python.exe'))

# Relaunch with venv Python if not already using it
if os.path.exists(VENV_PYTHON) and os.path.abspath(sys.executable) != VENV_PYTHON:
    print(f"[INFO] Relaunching with virtual environment Python: {VENV_PYTHON}")
    args = [VENV_PYTHON] + sys.argv
    os.execv(VENV_PYTHON, args)

# Step 1: Initialize database only if it doesn't exist
if not os.path.exists(DB_PATH):
    print("Creating new database...")
    try:
        subprocess.run([sys.executable, CREATE_DB_PATH], check=True)
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
    subprocess.run([sys.executable, APP_PATH])
except KeyboardInterrupt:
    print("\n" + "="*50)
    print("Server stopped by user (Ctrl+C)")
    print("Thank you for using the Blood Donation Management System!")
    print("="*50)
except Exception as e:
    print(f"\nError starting the Flask app: {e}")
    sys.exit(1)
