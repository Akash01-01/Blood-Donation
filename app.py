from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_finder.db'
db = SQLAlchemy(app)

# Donor model (includes user info)
class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    availability = db.Column(db.Boolean, default=True)

# Receiver model (includes user info)
class Receiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)

# Admin model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        location = request.form.get('location', '')
        contact = request.form.get('contact', '')
        
        if role == 'donor':
            # Get donor-specific fields
            age = int(request.form.get('age', 0))
            gender = request.form.get('gender', '')
            blood_group = request.form.get('blood_group', '')
            
            # Create complete donor entry
            donor = Donor(
                name=name, 
                email=email, 
                password=password, 
                age=age, 
                gender=gender, 
                blood_group=blood_group, 
                location=location, 
                contact=contact
            )
            db.session.add(donor)
            db.session.commit()
            session['user_id'] = donor.id
            session['role'] = 'donor'
            return redirect('/donor-dashboard')
            
        elif role == 'receiver':
            # Create complete receiver entry
            receiver = Receiver(
                name=name, 
                email=email, 
                password=password, 
                location=location, 
                contact=contact
            )
            db.session.add(receiver)
            db.session.commit()
            session['user_id'] = receiver.id
            session['role'] = 'receiver'
            return redirect('/receiver-dashboard')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check in all tables
        donor = Donor.query.filter_by(email=email).first()
        receiver = Receiver.query.filter_by(email=email).first()
        admin = Admin.query.filter_by(email=email).first()
        
        user = donor or receiver or admin
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            
            if donor:
                session['role'] = 'donor'
                return redirect('/donor-dashboard')
            elif receiver:
                session['role'] = 'receiver'
                return redirect('/receiver-dashboard')
            elif admin:
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template('index.html')

@app.route('/donor-profile', methods=['GET', 'POST'])
def donor_profile():
    if request.method == 'POST':
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        location = request.form['location']
        contact = request.form['contact']
        
        # Update existing donor record
        donor = Donor.query.get(session['user_id'])
        donor.age = age
        donor.gender = gender
        donor.blood_group = blood_group
        donor.location = location
        donor.contact = contact
        db.session.commit()
        return redirect('/donor-dashboard')
    return render_template('donor_profile.html')

@app.route('/receiver-profile', methods=['GET', 'POST'])
def receiver_profile():
    if request.method == 'POST':
        location = request.form['location']
        contact = request.form['contact']
        
        # Update existing receiver record
        receiver = Receiver.query.get(session['user_id'])
        receiver.location = location
        receiver.contact = contact
        db.session.commit()
        return redirect('/receiver-dashboard')
    return render_template('receiver_profile.html')

# Admin dashboard route
@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('admin_dashboard.html')

# Admin login route (separate from regular login)
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        admin = Admin.query.filter_by(email=email).first()
        
        if admin and check_password_hash(admin.password, password):
            session['user_id'] = admin.id
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid admin credentials", 401
    return render_template('admin_login.html')

# Keep the old dashboard route for compatibility
@app.route('/dashboard')
def dashboard():
    return render_template('admin_dashboard.html')

# Function to create default admin (call this once)
def create_default_admin():
    with app.app_context():
        # Check if admin already exists
        admin = Admin.query.filter_by(email='admin@bloodfinder.com').first()
        if not admin:
            # Create default admin
            admin = Admin(
                name='Administrator',
                email='admin@bloodfinder.com',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin@bloodfinder.com / admin123")

if __name__ == '__main__':
    app.run(debug=True)
