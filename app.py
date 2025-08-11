

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_finder.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'donor' or 'receiver'
    donor = db.relationship('Donor', backref='user', uselist=False)
    receiver = db.relationship('Receiver', backref='user', uselist=False)

# Donor model
class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    availability = db.Column(db.Boolean, default=True)

# Receiver model
class Receiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

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
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered. Please use a different email.", 400
        user = User(name=name, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['role'] = role
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))
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
        donor = Donor(user_id=session['user_id'], age=age, gender=gender, blood_group=blood_group, location=location, contact=contact)
        db.session.add(donor)
        db.session.commit()
        return redirect('/donor-dashboard')
    return render_template('donor_profile.html')

@app.route('/receiver-profile', methods=['GET', 'POST'])
def receiver_profile():
    if request.method == 'POST':
        location = request.form['location']
        contact = request.form['contact']
        receiver = Receiver(user_id=session['user_id'], location=location, contact=contact)
        db.session.add(receiver)
        db.session.commit()
        return redirect('/receiver-dashboard')
    return render_template('receiver_profile.html')


# Admin dashboard route
@app.route('/dashboard')
def dashboard():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)
