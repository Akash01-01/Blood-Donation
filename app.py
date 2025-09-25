from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_finder.db'
db = SQLAlchemy(app)

# Free Geocoding Functions
def geocode_address_free(address):
    """
    Convert address to coordinates using FREE Nominatim service
    No API key required, completely free
    """
    try:
        # Initialize free geocoder
        geolocator = Nominatim(user_agent="blood_donation_system_v1")
        
        # Add small delay to respect rate limits (1 per second)
        time.sleep(1.1)
        
        # Geocode the address
        location = geolocator.geocode(address, timeout=10)
        
        if location:
            return {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'full_address': location.address,
                'success': True
            }
        else:
            return {'success': False, 'error': 'Address not found'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def calculate_distance_free(lat1, lon1, lat2, lon2):
    """
    Calculate distance using free geopy library
    Returns distance in kilometers
    """
    try:
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        
        # Calculate distance using geodesic (most accurate)
        distance = geodesic(point1, point2).kilometers
        
        return round(distance, 2)
    except:
        return None

def reverse_geocode_free(lat, lon):
    """
    Convert coordinates to address using FREE Nominatim service
    """
    try:
        geolocator = Nominatim(user_agent="blood_donation_system_v1")
        time.sleep(1.1)
        
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        
        if location:
            return {
                'address': location.address,
                'success': True
            }
        else:
            return {'success': False, 'error': 'Location not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

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
    # Location coordinates for distance-based search
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    geocoded = db.Column(db.Boolean, default=False)
    last_geocoded = db.Column(db.DateTime, nullable=True)

# Receiver model (includes user info)
class Receiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    # Location coordinates for distance-based search
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    geocoded = db.Column(db.Boolean, default=False)
    last_geocoded = db.Column(db.DateTime, nullable=True)

# Donation History model
class DonationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    donation_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    blood_type = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.String(20), nullable=False)  # e.g., "450ml", "1 unit"
    location = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Completed')  # Completed, Pending, Cancelled
    notes = db.Column(db.Text)

# Blood Request model
class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('receiver.id'), nullable=False)
    blood_group_needed = db.Column(db.String(5), nullable=False)
    quantity_needed = db.Column(db.String(20), nullable=False)
    urgency = db.Column(db.String(20), nullable=False, default='Normal')  # Critical, High, Normal, Low
    hospital_name = db.Column(db.String(200), nullable=False)
    hospital_location = db.Column(db.String(200), nullable=False)
    request_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    needed_by_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active')  # Active, Fulfilled, Cancelled, Expired
    contact_person = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    additional_notes = db.Column(db.Text)
    
    # Relationship to get receiver info
    receiver = db.relationship('Receiver', backref=db.backref('blood_requests', lazy=True))

# Donation Response model (when donors respond to requests)
class DonationResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('blood_request.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    response_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending, Confirmed, Completed, Cancelled
    donor_notes = db.Column(db.Text)
    
    # Relationships
    blood_request = db.relationship('BloodRequest', backref=db.backref('responses', lazy=True))
    donor = db.relationship('Donor', backref=db.backref('donation_responses', lazy=True))

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
            
            # Geocode location in background (optional - don't block signup)
            try:
                geocode_result = geocode_address_free(location)
                if geocode_result['success']:
                    donor.latitude = geocode_result['latitude']
                    donor.longitude = geocode_result['longitude']
                    donor.geocoded = True
                    donor.last_geocoded = datetime.now()
            except:
                pass  # Don't fail signup if geocoding fails
            
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
            
            # Geocode location in background (optional - don't block signup)
            try:
                geocode_result = geocode_address_free(location)
                if geocode_result['success']:
                    receiver.latitude = geocode_result['latitude']
                    receiver.longitude = geocode_result['longitude']
                    receiver.geocoded = True
                    receiver.last_geocoded = datetime.now()
            except:
                pass  # Don't fail signup if geocoding fails
            
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
            session['user_email'] = email  # Store email for role switching
            
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

@app.route('/donor-dashboard')
def donor_dashboard():
    if session.get('role') != 'donor':
        return redirect('/')
    
    donor = Donor.query.get(session['user_id'])
    if not donor:
        return redirect('/logout')
    
    # Get donation history
    donation_history = DonationHistory.query.filter_by(donor_id=donor.id).order_by(DonationHistory.donation_date.desc()).all()
    
    # Get active blood requests that match donor's blood type
    compatible_requests = BloodRequest.query.filter_by(
        blood_group_needed=donor.blood_group,
        status='Active'
    ).order_by(BloodRequest.needed_by_date.asc()).all()
    
    # Get donor's responses to requests
    donor_responses = DonationResponse.query.filter_by(donor_id=donor.id).order_by(DonationResponse.response_date.desc()).all()
    
    # Calculate stats
    total_donations = len(donation_history)
    pending_responses = len([r for r in donor_responses if r.status == 'Pending'])
    
    return render_template('donor_dashboard.html', 
                         donor=donor,
                         donation_history=donation_history,
                         compatible_requests=compatible_requests,
                         donor_responses=donor_responses,
                         total_donations=total_donations,
                         pending_responses=pending_responses)

@app.route('/receiver-dashboard')
def receiver_dashboard():
    if session.get('role') != 'receiver':
        return redirect('/')
    
    receiver = Receiver.query.get(session['user_id'])
    if not receiver:
        return redirect('/logout')
    
    # Get receiver's blood requests
    blood_requests = BloodRequest.query.filter_by(receiver_id=receiver.id).order_by(BloodRequest.request_date.desc()).all()
    
    # Get responses to receiver's requests
    request_responses = []
    for request in blood_requests:
        responses = DonationResponse.query.filter_by(request_id=request.id).all()
        request_responses.extend(responses)
    
    # Calculate stats
    active_requests = len([r for r in blood_requests if r.status == 'Active'])
    total_requests = len(blood_requests)
    received_responses = len(request_responses)
    
    return render_template('receiver_dashboard.html', 
                         receiver=receiver,
                         blood_requests=blood_requests,
                         request_responses=request_responses,
                         active_requests=active_requests,
                         total_requests=total_requests,
                         received_responses=received_responses)

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
    donors = Donor.query.all()
    receivers = Receiver.query.all()
    
    # Calculate stats for dashboard
    total_donors = len(donors)
    total_receivers = len(receivers)
    available_donors = len([d for d in donors if d.availability])
    
    return render_template('admin_dashboard.html', 
                         donors=donors, 
                         receivers=receivers,
                         total_donors=total_donors,
                         total_receivers=total_receivers,
                         available_donors=available_donors)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

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

# Receiver: Enhanced Search Donors with Distance-based Filtering
@app.route('/search-donors', methods=['GET', 'POST'])
def search_donors():
    donors = []
    location = ''
    blood_group = ''
    radius = 10
    user_lat = None
    user_lon = None
    show_distance = False
    
    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        radius = int(request.form.get('radius', 10))
        user_lat = request.form.get('user_lat')
        user_lon = request.form.get('user_lon')
        
        # Start with base query - only available donors
        query = Donor.query.filter(Donor.availability == True)
        
        # Filter by blood group if specified
        if blood_group:
            query = query.filter(Donor.blood_group == blood_group)
        
        donors = query.all()
        
        # Handle location-based filtering
        recipient_lat = None
        recipient_lon = None
        
        # Priority 1: Use GPS coordinates if provided
        if user_lat and user_lon:
            try:
                recipient_lat = float(user_lat)
                recipient_lon = float(user_lon)
                show_distance = True
            except:
                pass
        
        # Priority 2: Geocode text location if no GPS coordinates
        elif location:
            geocode_result = geocode_address_free(location)
            if geocode_result['success']:
                recipient_lat = geocode_result['latitude']
                recipient_lon = geocode_result['longitude']
                show_distance = True
        
        # If we have recipient coordinates, filter by distance
        if recipient_lat and recipient_lon:
            donors_with_distance = []
            
            for donor in donors:
                # Geocode donor if not already done
                if not donor.geocoded or not donor.latitude or not donor.longitude:
                    donor_geocode = geocode_address_free(donor.location)
                    if donor_geocode['success']:
                        donor.latitude = donor_geocode['latitude']
                        donor.longitude = donor_geocode['longitude']
                        donor.geocoded = True
                        donor.last_geocoded = datetime.now()
                        db.session.commit()
                
                # Calculate distance if donor has coordinates
                if donor.latitude and donor.longitude:
                    distance = calculate_distance_free(
                        recipient_lat, recipient_lon,
                        donor.latitude, donor.longitude
                    )
                    
                    if distance and distance <= radius:
                        donor.distance = distance
                        donors_with_distance.append(donor)
            
            # Sort by distance (nearest first)
            donors_with_distance.sort(key=lambda x: x.distance)
            donors = donors_with_distance
        
        # If no location provided, show all matching donors
        elif not location and not user_lat:
            # Just filter by blood group if no location provided
            pass
    
    return render_template('search_donors.html', 
                         donors=donors, 
                         location=location, 
                         blood_group=blood_group,
                         radius=radius,
                         show_distance=show_distance)

# API: Reverse Geocoding for "Use My Location" feature
@app.route('/api/reverse-geocode', methods=['POST'])
def api_reverse_geocode():
    data = request.get_json()
    lat = data.get('latitude')
    lon = data.get('longitude')
    
    if not lat or not lon:
        return jsonify({'success': False, 'error': 'Coordinates required'})
    
    result = reverse_geocode_free(lat, lon)
    return jsonify(result)

# Admin: Edit Donor
@app.route('/admin/edit-donor/<int:donor_id>', methods=['GET', 'POST'])
def admin_edit_donor(donor_id):
    if session.get('role') != 'admin':
        return redirect('/')
    donor = Donor.query.get_or_404(donor_id)
    if request.method == 'POST':
        donor.name = request.form['name']
        donor.email = request.form['email']
        donor.age = request.form['age']
        donor.gender = request.form['gender']
        donor.blood_group = request.form['blood_group']
        donor.location = request.form['location']
        donor.contact = request.form['contact']
        donor.availability = 'availability' in request.form
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit_donor.html', donor=donor)

# Admin: Delete Donor
@app.route('/admin/delete-donor/<int:donor_id>', methods=['POST'])
def admin_delete_donor(donor_id):
    if session.get('role') != 'admin':
        return redirect('/')
    donor = Donor.query.get_or_404(donor_id)
    db.session.delete(donor)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Admin: Edit Receiver
@app.route('/admin/edit-receiver/<int:receiver_id>', methods=['GET', 'POST'])
def admin_edit_receiver(receiver_id):
    if session.get('role') != 'admin':
        return redirect('/')
    receiver = Receiver.query.get_or_404(receiver_id)
    if request.method == 'POST':
        receiver.name = request.form['name']
        receiver.email = request.form['email']
        receiver.location = request.form['location']
        receiver.contact = request.form['contact']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit_receiver.html', receiver=receiver)

# Admin: Delete Receiver
@app.route('/admin/delete-receiver/<int:receiver_id>', methods=['POST'])
def admin_delete_receiver(receiver_id):
    if session.get('role') != 'admin':
        return redirect('/')
    receiver = Receiver.query.get_or_404(receiver_id)
    db.session.delete(receiver)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Role switching route
@app.route('/switch-role', methods=['POST'])
def switch_role():
    if 'user_id' not in session or 'user_email' not in session:
        return redirect('/')
    
    new_role = request.form.get('role')
    current_role = session.get('role')
    user_email = session.get('user_email')
    
    # Get current user info
    current_user = None
    if current_role == 'donor':
        current_user = Donor.query.get(session['user_id'])
    elif current_role == 'receiver':
        current_user = Receiver.query.get(session['user_id'])
    
    if not current_user:
        return redirect('/logout')
    
    if new_role == 'donor':
        # Check if donor profile exists
        donor = Donor.query.filter_by(email=user_email).first()
        if not donor:
            # Create donor profile if switching from receiver
            if current_role == 'receiver':
                return redirect('/setup-donor-profile')
        else:
            session['role'] = 'donor'
            session['user_id'] = donor.id
            return redirect('/donor-dashboard')
    
    elif new_role == 'receiver':
        # Check if receiver profile exists
        receiver = Receiver.query.filter_by(email=user_email).first()
        if not receiver:
            # Create receiver profile if switching from donor
            if current_role == 'donor':
                return redirect('/setup-receiver-profile')
        else:
            session['role'] = 'receiver'
            session['user_id'] = receiver.id
            return redirect('/receiver-dashboard')
    
    # If switching is not possible, stay in current role
    if current_role == 'donor':
        return redirect('/donor-dashboard')
    elif current_role == 'receiver':
        return redirect('/receiver-dashboard')
    else:
        return redirect('/')

# Setup donor profile for users switching from receiver
@app.route('/setup-donor-profile', methods=['GET', 'POST'])
def setup_donor_profile():
    if 'user_email' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        # Get current receiver info to copy basic details
        receiver = Receiver.query.filter_by(email=session['user_email']).first()
        
        # Create new donor profile
        donor = Donor(
            name=receiver.name if receiver else request.form['name'],
            email=session['user_email'],
            password=receiver.password if receiver else '',
            age=int(request.form['age']),
            gender=request.form['gender'],
            blood_group=request.form['blood_group'],
            location=request.form['location'],
            contact=request.form['contact']
        )
        
        try:
            db.session.add(donor)
            db.session.commit()
            session['role'] = 'donor'
            session['user_id'] = donor.id
            return redirect('/donor-dashboard')
        except Exception as e:
            return f"Error creating donor profile: {e}", 500
    
    # Get current user info to pre-fill form
    current_user = Receiver.query.filter_by(email=session['user_email']).first()
    return render_template('setup_donor_profile.html', user=current_user)

# Setup receiver profile for users switching from donor
@app.route('/setup-receiver-profile', methods=['GET', 'POST'])
def setup_receiver_profile():
    if 'user_email' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        # Get current donor info to copy basic details
        donor = Donor.query.filter_by(email=session['user_email']).first()
        
        # Create new receiver profile
        receiver = Receiver(
            name=donor.name if donor else request.form['name'],
            email=session['user_email'],
            password=donor.password if donor else '',
            location=request.form['location'],
            contact=request.form['contact']
        )
        
        try:
            db.session.add(receiver)
            db.session.commit()
            session['role'] = 'receiver'
            session['user_id'] = receiver.id
            return redirect('/receiver-dashboard')
        except Exception as e:
            return f"Error creating receiver profile: {e}", 500
    
    # Get current user info to pre-fill form
    current_user = Donor.query.filter_by(email=session['user_email']).first()
    return render_template('setup_receiver_profile.html', user=current_user)

# Check if user can switch roles
@app.route('/check-role-availability/<role>')
def check_role_availability(role):
    if 'user_email' not in session:
        return {'available': False, 'message': 'Not logged in'}
    
    user_email = session['user_email']
    
    if role == 'donor':
        donor = Donor.query.filter_by(email=user_email).first()
        return {
            'available': donor is not None,
            'message': 'Donor profile exists' if donor else 'Need to setup donor profile'
        }
    elif role == 'receiver':
        receiver = Receiver.query.filter_by(email=user_email).first()
        return {
            'available': receiver is not None,
            'message': 'Recipient profile exists' if receiver else 'Need to setup recipient profile'
        }
    
    return {'available': False, 'message': 'Invalid role'}

# Add donation history
@app.route('/add-donation', methods=['GET', 'POST'])
def add_donation():
    if session.get('role') != 'donor':
        return redirect('/')
    
    if request.method == 'POST':
        donation = DonationHistory(
            donor_id=session['user_id'],
            blood_type=request.form['blood_type'],
            quantity=request.form['quantity'],
            location=request.form['location'],
            status=request.form.get('status', 'Completed'),
            notes=request.form.get('notes', '')
        )
        db.session.add(donation)
        db.session.commit()
        return redirect('/donor-dashboard')
    
    donor = Donor.query.get(session['user_id'])
    return render_template('add_donation.html', donor=donor)

# Create blood request
@app.route('/create-request', methods=['GET', 'POST'])
def create_request():
    if session.get('role') != 'receiver':
        return redirect('/')
    
    if request.method == 'POST':
        from datetime import datetime
        blood_request = BloodRequest(
            receiver_id=session['user_id'],
            blood_group_needed=request.form['blood_group_needed'],
            quantity_needed=request.form['quantity_needed'],
            urgency=request.form['urgency'],
            hospital_name=request.form['hospital_name'],
            hospital_location=request.form['hospital_location'],
            needed_by_date=datetime.strptime(request.form['needed_by_date'], '%Y-%m-%d'),
            contact_person=request.form['contact_person'],
            contact_number=request.form['contact_number'],
            additional_notes=request.form.get('additional_notes', '')
        )
        db.session.add(blood_request)
        db.session.commit()
        return redirect('/receiver-dashboard')
    
    return render_template('create_request.html')

# Respond to blood request
@app.route('/respond-to-request/<int:request_id>', methods=['POST'])
def respond_to_request(request_id):
    if session.get('role') != 'donor':
        return redirect('/')
    
    # Check if donor already responded
    existing_response = DonationResponse.query.filter_by(
        request_id=request_id,
        donor_id=session['user_id']
    ).first()
    
    if not existing_response:
        response = DonationResponse(
            request_id=request_id,
            donor_id=session['user_id'],
            donor_notes=request.form.get('notes', '')
        )
        db.session.add(response)
        db.session.commit()
    
    return redirect('/donor-dashboard')

# Update donation availability
@app.route('/toggle-availability', methods=['POST'])
def toggle_availability():
    if session.get('role') != 'donor':
        return redirect('/')
    
    donor = Donor.query.get(session['user_id'])
    donor.availability = not donor.availability
    db.session.commit()
    return redirect('/donor-dashboard')

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