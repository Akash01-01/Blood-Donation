# 🩸 Blood Donation Management System

A comprehensive Flask-based web application for managing blood donors and recipients, helping connect people in need of blood with available donors through an intuitive, modern interface.

## ✨ Enhanced Features

### 🔄 **Role Switching System**

- **Dual Role Support**: Users can seamlessly switch between Donor and Recipient roles
- **Toggle Control**: Easy role switching with a single button in the dashboard
- **Consistent UI**: Unified design language across all roles while maintaining role-specific functionality

### 👤 **Enhanced User Roles**

#### **Donor Dashboard**

- **Donation History Tracking**: Complete record of all blood donations
- **Add New Donations**: Easy form to record new donation activities
- **Blood Request Matching**: View blood requests that match donor's blood type
- **Availability Toggle**: Quick switch to update donation availability status
- **Response Management**: Track responses to blood requests from recipients

#### **Recipient Dashboard**

- **Blood Request Management**: Create and track blood requests with detailed information
- **Request History**: View all previous blood requests and their status
- **Donor Responses**: See all responses from donors to blood requests
- **Advanced Search**: Find donors by location and blood group with improved filtering
- **Request Analytics**: Track active requests, total requests, and received responses

#### **Admin Panel** (Enhanced)

- **Comprehensive User Management**: Manage donors and recipients with detailed controls
- **System Statistics**: Advanced dashboard with real-time metrics
- **User Activity Monitoring**: Track donation history and request patterns
- **Data Management**: Full CRUD operations for all user types

### 📊 **Advanced Features**

- **Smart Blood Matching**: Automatic matching of blood requests with compatible donors
- **Priority System**: Critical, High, Normal, and Low priority levels for blood requests
- **Hospital Integration**: Track hospital information and contact details
- **Response Tracking**: Complete audit trail of donor responses to requests
- **Availability Management**: Real-time donor availability status

## Quick Start

### Method 1: Using the run script (Recommended)

```bash
python run.py
```

### Method 2: Direct Flask app

```bash
python app.py
```

Both methods will:

1. Create the database if it doesn't exist
2. Start the Flask development server
3. Make the app available at: http://127.0.0.1:5000

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Default Admin Account

- **Email**: admin@bloodfinder.com
- **Password**: admin123

## Project Structure

```
Blood-Donation/
├── app.py              # Main Flask application
├── run.py              # Startup script
├── create_db.py        # Database initialization
├── clean_db.py         # Database cleanup utility
├── instance/           # Database storage
│   └── blood_finder.db
├── templates/          # HTML templates
│   ├── index.html      # Home page
│   ├── signup.html     # User registration
│   ├── admin_dashboard.html
│   ├── donor_profile.html
│   ├── receiver_profile.html
│   └── search_donors.html
└── __pycache__/        # Python cache files
```

## 🚀 Usage Guide

### **Getting Started**

1. **Start the application** using `python run.py`
2. **Visit** http://127.0.0.1:5000 in your web browser
3. **Register** as a donor or recipient, or login as admin

### **For Donors**

1. **Complete Profile**: Add age, gender, blood group, and contact details
2. **Manage Availability**: Toggle availability status for donation
3. **Record Donations**: Add donation history with details
4. **Respond to Requests**: View and respond to matching blood requests
5. **Switch Roles**: Easily switch to recipient mode if needed

### **For Recipients**

1. **Create Blood Requests**: Submit detailed blood requirements
2. **Track Requests**: Monitor status and responses from donors
3. **Search Donors**: Find available donors by location and blood group
4. **Manage Communication**: Contact donors directly through provided information
5. **Switch Roles**: Switch to donor mode to help others

### **For Administrators**

1. **Monitor System**: View comprehensive dashboard with statistics
2. **Manage Users**: Add, edit, or remove donor and recipient accounts
3. **Oversee Requests**: Track all blood requests and donation activities
4. **System Analytics**: Monitor platform usage and effectiveness

### **Role Switching**

- Users can maintain both donor and recipient profiles simultaneously
- Easy one-click switching between roles using the dashboard toggle
- Role-specific interfaces with consistent design elements
- Seamless transition preserving user context and data

## 🗄️ Enhanced Database Models

### **Core User Models**

- **Donor**: Enhanced with age, gender, and detailed contact information
- **Receiver**: Recipient information with location and emergency contacts
- **Admin**: Administrative users with management capabilities

### **Activity Tracking Models**

- **DonationHistory**: Complete tracking of all blood donations
  - Donation date, blood type, quantity, location, status, notes
- **BloodRequest**: Comprehensive blood request management
  - Blood group needed, quantity, urgency level, hospital details
  - Contact person, needed by date, additional notes, status tracking
- **DonationResponse**: Donor response system
  - Response tracking, status management, donor notes

## 🎨 UI/UX Design

### **Design Consistency**

- **Unified Color Scheme**: Professional red and gray palette across all interfaces
- **Consistent Typography**: Inter font family for modern, readable interface
- **Component Harmony**: Matching buttons, forms, and navigation elements
- **Responsive Design**: Mobile-first approach with Tailwind CSS

### **Role-Specific Interfaces**

- **Visual Role Indicators**: Clear current role display with easy switching
- **Contextual Navigation**: Role-appropriate menu items and quick actions
- **Status Indicators**: Color-coded availability, urgency, and response status
- **Interactive Elements**: Hover effects, smooth transitions, and user feedback

### **Modern Features**

- **Dashboard Analytics**: Visual statistics and progress indicators
- **Smart Search**: Multi-criteria filtering with real-time results
- **Action Buttons**: Context-aware actions for each user type
- **Status Management**: Visual status indicators with easy updates

## Development Notes

- The application runs in debug mode for development
- Database is SQLite stored in `instance/blood_finder.db`
- Sessions are used for user authentication
- Passwords are hashed using Werkzeug security functions

## Important

- This is a development server - do not use in production
- For production deployment, use a proper WSGI server like Gunicorn
- Consider adding SSL/HTTPS for production use
- Add proper error handling and validation for production

## Troubleshooting

**Q: I see "KeyboardInterrupt" error**
A: This is normal - it happens when you press Ctrl+C to stop the server. It's not an actual error.

**Q: Database errors**
A: Try running `python clean_db.py` to reset the database, then `python create_db.py` to recreate it.

**Q: Port already in use**
A: Another Flask app might be running. Stop it or change the port in app.py.
