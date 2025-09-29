from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_finder.db'
db = SQLAlchemy(app)

# Free Geocoding Functions
def geocode_address_free(address):
    """
    Convert address to coordinates using FREE Nominatim service
    No API key required, completely free
    Enhanced for Indian addresses with fallback searches
    """
    try:
        # Initialize free geocoder
        geolocator = Nominatim(user_agent="blood_donation_system_v1")
        
        # Add small delay to respect rate limits (1 per second)
        time.sleep(1.1)
        
        # Try original address first
        location = geolocator.geocode(address, timeout=10)
        
        # If not found, try with ", India" appended
        if not location and ", India" not in address.lower():
            time.sleep(1.1)
            location = geolocator.geocode(f"{address}, India", timeout=10)
        
        # If still not found, try with ", Karnataka, India" for common Indian cities
        if not location and "karnataka" not in address.lower():
            time.sleep(1.1)
            location = geolocator.geocode(f"{address}, Karnataka, India", timeout=10)
        
        if location:
            return {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'full_address': location.address,
                'success': True
            }
        else:
            return {'success': False, 'error': f'Address "{address}" not found'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def calculate_distance_free(lat1, lon1, lat2, lon2):
    """
    Calculate distance using free geopy library
    Returns distance in kilometers with high precision
    """
    try:
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        
        # Calculate distance using geodesic (most accurate)
        distance = geodesic(point1, point2).kilometers
        
        # Round to 3 decimal places for higher precision
        return round(distance, 3)
    except Exception as e:
        print(f"Distance calculation error: {e}")
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
    
    # New fields for "requesting for" functionality
    requesting_for = db.Column(db.String(20), nullable=False, default='myself')  # 'myself' or 'someone_else'
    patient_name = db.Column(db.String(100))  # Only filled when requesting_for = 'someone_else'
    patient_relation = db.Column(db.String(50))  # Only filled when requesting_for = 'someone_else'
    
    # Relationship to get receiver info
    receiver = db.relationship('Receiver', backref=db.backref('blood_requests', lazy=True))

# Donation Response model (when donors respond to requests)
class DonationResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('blood_request.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    response_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending, Accepted, Rejected, Confirmed, Completed, Cancelled, Declined
    donor_notes = db.Column(db.Text)
    receiver_notes = db.Column(db.Text)  # Notes from receiver when managing responses
    scheduled_date = db.Column(db.Date, nullable=True)  # Date when donor plans to donate
    
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
    
    donor = db.session.get(Donor, session['user_id'])
    if not donor:
        return redirect('/logout')
    
    # Get donation history
    donation_history = DonationHistory.query.filter_by(donor_id=donor.id).order_by(DonationHistory.donation_date.desc()).all()
    
    # Get active blood requests that match donor's blood type
    # Logic: Show requests where this donor CAN donate to the requested blood type
    compatible_blood_groups = [donor.blood_group]  # Always include exact match
    
    # Add blood type compatibility rules - what blood types can this donor donate TO
    if donor.blood_group == 'O-':
        # O- is universal donor, can donate to anyone
        compatible_blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    elif donor.blood_group == 'O+':
        # O+ can donate to O+, A+, B+, AB+
        compatible_blood_groups = ['O+', 'A+', 'B+', 'AB+']
    elif donor.blood_group == 'A-':
        # A- can donate to A-, A+, AB-, AB+
        compatible_blood_groups = ['A-', 'A+', 'AB-', 'AB+']
    elif donor.blood_group == 'A+':
        # A+ can donate to A+, AB+
        compatible_blood_groups = ['A+', 'AB+']
    elif donor.blood_group == 'B-':
        # B- can donate to B-, B+, AB-, AB+
        compatible_blood_groups = ['B-', 'B+', 'AB-', 'AB+']
    elif donor.blood_group == 'B+':
        # B+ can donate to B+, AB+
        compatible_blood_groups = ['B+', 'AB+']
    elif donor.blood_group == 'AB-':
        # AB- can donate to AB-, AB+
        compatible_blood_groups = ['AB-', 'AB+']
    elif donor.blood_group == 'AB+':
        # AB+ can only donate to AB+
        compatible_blood_groups = ['AB+']
    
    # Get donor's responses to requests first
    donor_responses = DonationResponse.query.filter_by(donor_id=donor.id).order_by(DonationResponse.response_date.desc()).all()
    
    # Get request IDs that this donor has already responded to
    responded_request_ids = [response.request_id for response in donor_responses]
    
    # Get compatible requests excluding those the donor has already responded to
    query = BloodRequest.query.filter(
        BloodRequest.blood_group_needed.in_(compatible_blood_groups),
        BloodRequest.status == 'Active'
    )
    
    # Exclude requests that the donor has already responded to (accepted/declined/etc.)
    if responded_request_ids:
        query = query.filter(~BloodRequest.id.in_(responded_request_ids))
    
    compatible_requests = query.order_by(BloodRequest.urgency.desc(), BloodRequest.needed_by_date.asc()).all()
    
    # Calculate stats
    total_donations = len(donation_history)
    pending_responses = len([r for r in donor_responses if r.status == 'Pending'])
    
    return render_template('donor_dashboard.html', 
                         donor=donor,
                         donation_history=donation_history,
                         compatible_requests=compatible_requests,
                         donor_responses=donor_responses,
                         total_donations=total_donations,
                         pending_responses=pending_responses,
                         current_date=datetime.now().date(),
                         timedelta=timedelta)

@app.route('/receiver-dashboard')
def receiver_dashboard():
    if session.get('role') != 'receiver':
        return redirect('/')
    
    receiver = db.session.get(Receiver, session['user_id'])
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
        donor = db.session.get(Donor, session['user_id'])
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
        receiver = db.session.get(Receiver, session['user_id'])
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
        
        # Debug: Log the received parameters
        print(f"Search params: location='{location}', blood_group='{blood_group}', radius={radius}km")
        if user_lat and user_lon:
            print(f"GPS coordinates: lat={user_lat}, lon={user_lon}")
        
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
                print(f"Using GPS coordinates: {recipient_lat}, {recipient_lon}")
            except:
                print("Failed to parse GPS coordinates")
        
        # Priority 2: Geocode text location if no GPS coordinates
        elif location:
            geocode_result = geocode_address_free(location)
            if geocode_result['success']:
                recipient_lat = geocode_result['latitude']
                recipient_lon = geocode_result['longitude']
                show_distance = True
            else:
                # Fallback: Simple text-based location search if geocoding fails
                location_lower = location.lower().strip()
                filtered_donors = []
                for donor in donors:
                    donor_location_lower = donor.location.lower().strip()
                    # Check if search location is contained in donor location or vice versa
                    if (location_lower in donor_location_lower or 
                        donor_location_lower in location_lower or
                        any(word in donor_location_lower for word in location_lower.split() if len(word) > 2)):
                        filtered_donors.append(donor)
                donors = filtered_donors
        
        # If we have recipient coordinates, filter by distance
        if recipient_lat and recipient_lon:
            donors_with_distance = []
            donors_without_coordinates = []
            
            print(f"📍 GPS Search: Lat={recipient_lat}, Lon={recipient_lon}, Radius={radius}km")
            print(f"Filtering {len(donors)} donors by distance from GPS location...")
            
            for donor in donors:
                # Geocode donor if not already done
                if not donor.geocoded or not donor.latitude or not donor.longitude:
                    print(f"🔍 Geocoding donor: {donor.name} - {donor.location}")
                    donor_geocode = geocode_address_free(donor.location)
                    if donor_geocode['success']:
                        donor.latitude = donor_geocode['latitude']
                        donor.longitude = donor_geocode['longitude']
                        donor.geocoded = True
                        donor.last_geocoded = datetime.now()
                        try:
                            db.session.commit()
                            print(f"✅ Geocoded {donor.name}: {donor.latitude}, {donor.longitude}")
                        except Exception as e:
                            print(f"❌ Database error for {donor.name}: {e}")
                            db.session.rollback()
                    else:
                        print(f"❌ Failed to geocode {donor.name} - {donor_geocode.get('error', 'Unknown error')}")
                
                # Calculate distance if donor has coordinates
                if donor.latitude and donor.longitude:
                    distance = calculate_distance_free(
                        recipient_lat, recipient_lon,
                        donor.latitude, donor.longitude
                    )
                    
                    print(f"📏 {donor.name} ({donor.location}): {distance}km away (limit: {radius}km)")
                    print(f"   🗺️  Donor coords: ({donor.latitude}, {donor.longitude})")
                    print(f"   📍 Your coords: ({recipient_lat}, {recipient_lon})")
                    
                    if distance is not None and distance <= radius:
                        donor.distance = distance
                        donors_with_distance.append(donor)
                        print(f"✅ INCLUDED: {donor.name} - {distance}km (within {radius}km radius)")
                    else:
                        print(f"❌ EXCLUDED: {donor.name} - {distance}km (outside {radius}km radius)")
                else:
                    print(f"⚠️  No coordinates for {donor.name}")
                    print(f"   📍 Failed to geocode: {donor.location}")
                    # Only include non-geocoded donors if no GPS coordinates are used (manual search)
                    if not (user_lat and user_lon):
                        donor.distance = None
                        donors_without_coordinates.append(donor)
                        print(f"✅ INCLUDED: {donor.name} - no coordinates but manual search mode")
                    else:
                        print(f"❌ EXCLUDED: {donor.name} - no coordinates in GPS search mode")
            
            # Combine donors: first those with distance (sorted), then those without coordinates
            donors_with_distance.sort(key=lambda x: x.distance)
            donors = donors_with_distance + donors_without_coordinates
            
            # Double-check: verify all included donors are actually within radius
            verified_donors = []
            for donor in donors_with_distance:
                if hasattr(donor, 'distance') and donor.distance is not None:
                    if donor.distance <= radius:
                        verified_donors.append(donor)
                        print(f"✅ VERIFIED: {donor.name} - {donor.distance}km ✓")
                    else:
                        print(f"🚨 REMOVED: {donor.name} - {donor.distance}km (somehow exceeded radius)")
            
            # Update final donor list
            donors = verified_donors + donors_without_coordinates
            
            print(f"🎯 FINAL RESULT: {len(donors)} donors total")
            print(f"   📍 {len(verified_donors)} verified within {radius}km")
            print(f"   ❓ {len(donors_without_coordinates)} without coordinates")
            
            if len(verified_donors) == 0 and len(donors_without_coordinates) == 0:
                print(f"⚠️  WARNING: No donors found within {radius}km radius!")
                print(f"📍 Recipient location: {recipient_lat}, {recipient_lon}")
                print("Consider increasing search radius or checking donor locations.")
        else:
            print("No GPS coordinates available, using basic search")
            # If no location provided, show all matching donors (already filtered by blood group)
    
    # Get current receiver info if logged in as receiver
    current_receiver = None
    if session.get('role') == 'receiver' and session.get('user_id'):
        current_receiver = db.session.get(Receiver, session['user_id'])
    
    return render_template('search_donors.html', 
                         donors=donors, 
                         location=location, 
                         blood_group=blood_group,
                         radius=radius,
                         show_distance=show_distance,
                         current_receiver=current_receiver)

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
        current_user = db.session.get(Donor, session['user_id'])
    elif current_role == 'receiver':
        current_user = db.session.get(Receiver, session['user_id'])
    
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
    
    donor = db.session.get(Donor, session['user_id'])
    return render_template('add_donation.html', donor=donor)

# Create blood request
@app.route('/create-request', methods=['GET', 'POST'])
def create_request():
    if session.get('role') != 'receiver':
        return redirect('/')
    
    if request.method == 'POST':
        from datetime import datetime
        
        # Get the requesting_for value
        requesting_for = request.form['requesting_for']
        patient_name = None
        patient_relation = None
        
        # If requesting for someone else, get patient details
        if requesting_for == 'someone_else':
            patient_name = request.form.get('patient_name', '').strip()
            patient_relation = request.form.get('patient_relation', '')
        
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
            additional_notes=request.form.get('additional_notes', ''),
            requesting_for=requesting_for,
            patient_name=patient_name,
            patient_relation=patient_relation
        )
        db.session.add(blood_request)
        db.session.commit()
        
        # Send notification to compatible donors (you can enhance this further)
        print(f"🩸 New {blood_request.blood_group_needed} blood request created by {request.form['contact_person']}")
        print(f"📍 Location: {blood_request.hospital_location}")
        print(f"🚨 Urgency: {blood_request.urgency}")
        
        return redirect('/receiver-dashboard')
    
    # Pass datetime for template use
    from datetime import datetime, timedelta
    today = datetime.now()
    min_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render_template('create_request.html', min_date=min_date)

# Respond to blood request (Accept/Reject)
@app.route('/respond-to-request/<int:request_id>', methods=['POST'])
def respond_to_request(request_id):
    if session.get('role') != 'donor':
        return redirect('/')
    
    action = request.form.get('action', 'accept')  # accept, reject, or completed
    notes = request.form.get('notes', '')
    
    # Check if donor already responded
    existing_response = DonationResponse.query.filter_by(
        request_id=request_id,
        donor_id=session['user_id']
    ).first()
    
    if existing_response:
        # Update existing response
        if action == 'completed':
            existing_response.status = 'Completed'
            # Add to donation history
            blood_request = db.session.get(BloodRequest, request_id)
            donation = DonationHistory(
                donor_id=session['user_id'],
                blood_type=blood_request.blood_group_needed,
                quantity=blood_request.quantity_needed,
                donation_date=datetime.now(),
                location=blood_request.hospital_location,
                notes=f"Donated to {blood_request.contact_person} at {blood_request.hospital_name}"
            )
            db.session.add(donation)
        else:
            existing_response.status = 'Accepted' if action == 'accept' else 'Rejected'
        
        existing_response.donor_notes = notes
        existing_response.response_date = datetime.now()
        db.session.commit()
        print(f"🔄 Updated response: {existing_response.status}")
    else:
        # Create new response
        status = 'Accepted' if action == 'accept' else 'Rejected'
        response = DonationResponse(
            request_id=request_id,
            donor_id=session['user_id'],
            status=status,
            donor_notes=notes
        )
        
        db.session.add(response)
        db.session.commit()
        
        # Log the response for debugging
        blood_request = db.session.get(BloodRequest, request_id)
        print(f"🩸 {status} request: {blood_request.contact_person} needs {blood_request.blood_group_needed}")
    
    # Check if this is an AJAX request
    if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True, 
            'action': action,
            'message': f'Request {"accepted" if action == "accept" else "declined" if action == "reject" else "completed"} successfully'
        })
    
    return redirect('/donor-dashboard')

# Delete blood request
@app.route('/delete-request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if session.get('role') != 'receiver':
        return redirect('/')
    
    blood_request = BloodRequest.query.get_or_404(request_id)
    
    # Check if request belongs to current user
    if blood_request.receiver_id != session['user_id']:
        return redirect('/receiver-dashboard')
    
    # Delete associated responses first
    DonationResponse.query.filter_by(request_id=request_id).delete()
    
    # Delete the request
    db.session.delete(blood_request)
    db.session.commit()
    
    print(f"🗑️ Deleted request: {blood_request.blood_group_needed} blood request")
    return redirect('/receiver-dashboard')

# Clear all requests for user
@app.route('/clear-all-requests', methods=['POST'])
def clear_all_requests():
    if session.get('role') != 'receiver':
        return redirect('/')
    
    receiver_id = session['user_id']
    
    # Get all user's requests
    user_requests = BloodRequest.query.filter_by(receiver_id=receiver_id).all()
    
    # Delete all associated responses
    for req in user_requests:
        DonationResponse.query.filter_by(request_id=req.id).delete()
    
    # Delete all requests
    BloodRequest.query.filter_by(receiver_id=receiver_id).delete()
    db.session.commit()
    
    print(f"🧹 Cleared all requests for user {receiver_id}")
    return redirect('/receiver-dashboard')

# Manage donation response (cancel scheduled donation)
@app.route('/manage-donation-response/<int:response_id>', methods=['POST'])
def manage_donation_response(response_id):
    if session.get('role') != 'donor':
        return redirect('/')
    
    donation_response = DonationResponse.query.get_or_404(response_id)
    
    # Check if response belongs to current donor
    if donation_response.donor_id != session['user_id']:
        return redirect('/donor-dashboard')
    
    action = request.form.get('action', '')
    
    if action == 'cancel':
        donation_response.status = 'Cancelled'
        donation_response.donor_notes += f"\n[Cancelled by donor on {datetime.now().strftime('%m/%d/%Y')}]"
        db.session.commit()
        print(f"❌ Cancelled scheduled donation: Response ID {response_id}")
    
    return redirect('/donor-dashboard')

# Update response status (for managing existing responses)
@app.route('/update-response/<int:response_id>', methods=['POST'])
def update_response(response_id):
    if session.get('role') != 'donor':
        return redirect('/')
    
    response = DonationResponse.query.filter_by(
        id=response_id,
        donor_id=session['user_id']
    ).first()
    
    if response:
        new_status = request.form.get('status')
        if new_status in ['Accepted', 'Rejected', 'Confirmed', 'Completed', 'Cancelled']:
            response.status = new_status
            if request.form.get('notes'):
                response.donor_notes = request.form.get('notes')
            db.session.commit()
    
    return redirect('/donor-dashboard')

# Recipient: Accept or reject donor response
@app.route('/manage-donor-response/<int:response_id>', methods=['POST'])
def manage_donor_response(response_id):
    if session.get('role') != 'receiver':
        return redirect('/')
    
    response = DonationResponse.query.get_or_404(response_id)
    
    # Verify this response belongs to receiver's request
    if response.blood_request.receiver_id != session['user_id']:
        return redirect('/receiver-dashboard')
    
    action = request.form.get('action')  # confirm or decline
    
    if action == 'confirm':
        response.status = 'Confirmed'
        # Also update the blood request status if this is the chosen donor
        blood_request = response.blood_request
        blood_request.status = 'Fulfilled'
        
        # Cancel other pending responses for this request
        other_responses = DonationResponse.query.filter(
            DonationResponse.request_id == response.request_id,
            DonationResponse.id != response_id,
            DonationResponse.status.in_(['Pending', 'Accepted'])
        ).all()
        
        for other_response in other_responses:
            other_response.status = 'Cancelled'
        
    elif action == 'decline':
        response.status = 'Declined'
    
    if request.form.get('notes'):
        # Add receiver notes to the response
        response.receiver_notes = request.form.get('notes', '')
    
    db.session.commit()
    return redirect('/receiver-dashboard')

# Update donation availability
@app.route('/toggle-availability', methods=['POST'])
def toggle_availability():
    if session.get('role') != 'donor':
        return redirect('/')
    
    donor = db.session.get(Donor, session['user_id'])
    donor.availability = not donor.availability
    db.session.commit()
    return redirect('/donor-dashboard')

# View detailed blood request with responses (for recipients)
@app.route('/view-request/<int:request_id>')
def view_request(request_id):
    if session.get('role') != 'receiver':
        return redirect('/')
    
    blood_request = BloodRequest.query.filter_by(
        id=request_id,
        receiver_id=session['user_id']
    ).first_or_404()
    
    # Get all responses for this request
    responses = DonationResponse.query.filter_by(request_id=request_id)\
        .order_by(DonationResponse.response_date.desc()).all()
    
    return render_template('view_request.html', 
                         blood_request=blood_request, 
                         responses=responses)

# Donor responses management page
@app.route('/my-responses')
def my_responses():
    if session.get('role') != 'donor':
        return redirect('/')
    
    # Get only non-declined responses for display (declined responses are kept for filtering but hidden)
    responses = DonationResponse.query.filter(
        DonationResponse.donor_id == session['user_id'],
        ~DonationResponse.status.in_(['Rejected', 'Declined'])
    ).order_by(DonationResponse.response_date.desc()).all()
    
    print(f"📋 Showing {len(responses)} visible responses for donor {session['user_id']} (declined responses hidden)")
    
    return render_template('donor_responses.html', responses=responses)

# Clear visible responses (keep declined responses for filtering)
@app.route('/clear-all-responses', methods=['POST', 'GET'])
def clear_all_responses():
    print(f"🔍 Clear visible responses called")
    print(f"   Role: {session.get('role')}")
    print(f"   User ID: {session.get('user_id')}")
    
    # For testing, allow GET requests to show debug info
    if request.method == 'GET':
        return f"Session info: {dict(session)}, Role: {session.get('role')}, User ID: {session.get('user_id')}"
    
    if session.get('role') != 'donor':
        print("❌ Access denied - not a donor")
        return jsonify({'success': False, 'message': 'Access denied'})
    
    if not session.get('user_id'):
        print("❌ No user ID in session")
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    try:
        donor_id = session['user_id']
        print(f"🔍 Processing clear request for donor {donor_id}")
        
        # Only delete non-declined responses (keep declined/rejected for filtering)
        responses_to_keep = ['Rejected', 'Declined']  # Keep these for dashboard filtering
        responses_to_delete = DonationResponse.query.filter(
            DonationResponse.donor_id == donor_id,
            ~DonationResponse.status.in_(responses_to_keep)
        ).all()
        
        print(f"📋 Found {len(responses_to_delete)} non-declined responses to clear")
        
        if len(responses_to_delete) == 0:
            print("ℹ️ No clearable responses found")
            return jsonify({
                'success': True, 
                'message': 'No responses to clear (declined responses are kept for filtering)',
                'deleted_count': 0
            })
        
        # Delete only non-declined responses
        deleted_count = DonationResponse.query.filter(
            DonationResponse.donor_id == donor_id,
            ~DonationResponse.status.in_(responses_to_keep)
        ).delete()
        db.session.commit()
        
        print(f"🗑️ Successfully cleared {deleted_count} responses (kept declined responses for filtering)")
        
        return jsonify({
            'success': True, 
            'message': f'Successfully cleared {deleted_count} responses',
            'deleted_count': deleted_count
        })
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error clearing responses: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Failed to clear responses: {str(e)}'})

# Debug route to test clearing
@app.route('/debug-clear')
def debug_clear():
    if session.get('role') != 'donor':
        return f"Not logged in as donor. Current session: {dict(session)}"
    
    donor_id = session['user_id']
    responses = DonationResponse.query.filter_by(donor_id=donor_id).all()
    return f"Donor {donor_id} has {len(responses)} responses: {[r.id for r in responses]}"

# Send direct request to specific donor
@app.route('/send-request-to-donor/<int:donor_id>', methods=['GET', 'POST'])
def send_request_to_donor(donor_id):
    if session.get('role') != 'receiver':
        return redirect('/')
    
    donor = Donor.query.get_or_404(donor_id)
    receiver = db.session.get(Receiver, session['user_id'])
    
    if request.method == 'POST':
        from datetime import datetime
        
        # Create blood request targeted for this specific donor
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
            additional_notes=request.form.get('additional_notes', '') + f"\n\n[Direct request sent to: {donor.name}]"
        )
        
        # Debug: Log what contact person is being saved
        print(f"📝 Creating request with contact_person: '{request.form['contact_person']}'")
        print(f"📝 Receiver name: '{receiver.name}'")
        db.session.add(blood_request)
        db.session.commit()
        
        # Automatically create a pending response from the targeted donor
        auto_response = DonationResponse(
            request_id=blood_request.id,
            donor_id=donor_id,
            status='Pending',
            donor_notes=f"Direct request received from {receiver.name}. Please respond."
        )
        db.session.add(auto_response)
        db.session.commit()
        
        print(f"📨 Direct request sent from {receiver.name} to {donor.name}")
        return redirect('/receiver-dashboard')
    
    # Pass datetime for template use
    from datetime import datetime, timedelta
    today = datetime.now()
    min_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render_template('send_request_to_donor.html', 
                         donor=donor, 
                         receiver=receiver,
                         min_date=min_date)

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