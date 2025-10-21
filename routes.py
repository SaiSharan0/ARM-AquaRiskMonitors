from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Case, Disease, Location, Alert, EnvironmentalData, Recipient, SMSHistory
import json
import os

# Try to import Twilio, but make it optional
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
    print("✅ Twilio imported successfully - SMS features enabled")
except ImportError as e:
    TWILIO_AVAILABLE = False
    print(f"⚠️ Warning: Twilio not installed. SMS features will be disabled. Error: {e}")

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    # Remove landing page; send users directly to login
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.')
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'clinic')  # Default role is clinic
        
        # Validation
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('main.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('main.register'))
            
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('main.register'))
            
        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            return redirect(url_for('main.register'))
            
        # Create new user
        new_user = User(
            email=email,
            username=username,
            role=role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.')
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

@main.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime, timedelta
    
    # Get actual case count
    live_cases = Case.query.count()
    
    # Calculate active hotspots (locations with cases in the last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    active_locations = db.session.query(Location).join(Case).filter(
        Case.case_date >= thirty_days_ago
    ).distinct().count()
    
    active_hotspots = active_locations
    
    # Calculate overall water quality based on environmental data
    # This is simplified - in a real app, this would be more complex
    env_data = EnvironmentalData.query.order_by(EnvironmentalData.timestamp.desc()).first()
    
    if env_data and env_data.ph:
        if 6.5 <= env_data.ph <= 7.5:
            overall_water_quality = 'Good'
        elif 6.0 <= env_data.ph <= 8.0:
            overall_water_quality = 'Fair'
        else:
            overall_water_quality = 'Poor'
    else:
        overall_water_quality = 'Unknown'
    
    # Get all diseases
    diseases = Disease.query.all()
    
    # Create case distribution data
    labels = []
    data = []
    
    for disease in diseases:
        labels.append(disease.name)
        count = Case.query.filter_by(disease_id=disease.id).count()
        data.append(count)
    
    case_data = {
        "labels": labels,
        "data": data
    }
    
    # Get current datetime for template
    now = datetime.now()
    
    return render_template('dashboard.html', 
                          live_cases=live_cases,
                          active_hotspots=active_hotspots,
                          overall_water_quality=overall_water_quality,
                          case_data=json.dumps(case_data),
                          now=now)

@main.route('/report', methods=['GET', 'POST'])
@login_required
def report_case():
    if request.method == 'POST':
        disease_id = request.form.get('disease_id')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        symptoms = request.form.get('symptoms')
        num_cases = request.form.get('num_cases')

        # Create new location if it doesn't exist
        location = Location.query.filter_by(latitude=latitude, longitude=longitude).first()
        if not location:
            location = Location(latitude=latitude, longitude=longitude, name="Case Location")
            db.session.add(location)
            db.session.commit()

        new_case = Case(
            disease_id=disease_id,
            location_id=location.id,
            user_id=current_user.id,
            symptoms=symptoms,
            num_cases=num_cases
        )
        db.session.add(new_case)
        db.session.commit()
        flash('Case reported successfully!')
        return redirect(url_for('main.dashboard'))

    diseases = Disease.query.all()
    return render_template('report.html', diseases=diseases)

@main.route('/map')
@login_required
def map_view():
    from datetime import datetime
    
    # Get all cases with their related data
    cases = Case.query.all()
    
    # Group cases by location for the map
    case_locations = []
    case_by_location = {}
    
    for case in cases:
        loc_key = f"{case.location.latitude}:{case.location.longitude}"
        
        if loc_key in case_by_location:
            case_by_location[loc_key]['cases'] += case.num_cases
            # Update the disease if needed (in a real app, this would be more complex)
            if case.case_date > case_by_location[loc_key]['updated_date']:
                case_by_location[loc_key]['disease'] = case.disease.name
                case_by_location[loc_key]['updated_date'] = case.case_date
        else:
            case_by_location[loc_key] = {
                'lat': case.location.latitude,
                'lng': case.location.longitude,
                'name': case.location.name if case.location.name else f"Location at {case.location.latitude:.4f}, {case.location.longitude:.4f}",
                'disease': case.disease.name,
                'cases': case.num_cases,
                'updated_date': case.case_date
            }
    
    # Convert dictionary to list for template
    for loc_data in case_by_location.values():
        loc_data['updated'] = loc_data['updated_date'].strftime('%b %d, %Y')
        del loc_data['updated_date']  # Remove the datetime object before JSON serialization
        case_locations.append(loc_data)
        
    # Sort by number of cases, descending
    case_locations.sort(key=lambda x: x['cases'], reverse=True)
    
    return render_template('map_view.html', 
                          case_locations=case_locations,
                          caseLocations=case_locations)

@main.route('/trends')
@login_required
def trends():
    from datetime import datetime
    
    # More comprehensive placeholder data for trends analysis
    trend_data = {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "cholera_cases": [10, 12, 15, 20, 18, 25],
        "rainfall": [50, 60, 75, 80, 90, 110],
        "temperature": [24, 25, 27, 28, 29, 30],
        "turbidity": [15, 18, 25, 30, 28, 24],
        "ph": [6.8, 6.7, 6.5, 6.3, 6.4, 6.6],
        
        # Add additional data for correlation analysis
        "correlation": {
            "value": 0.78,
            "significance": "strong positive"
        },
        
        # Regional data
        "regions": {
            "guwahati": {"cases": 45, "rainfall": 80},
            "jorhat": {"cases": 32, "rainfall": 95},
            "dibrugarh": {"cases": 28, "rainfall": 105},
            "silchar": {"cases": 25, "rainfall": 115},
            "tezpur": {"cases": 18, "rainfall": 70}
        }
    }
    
    # Get current datetime for template
    now = datetime.now()
    
    return render_template('trends.html', 
                          trend_data=json.dumps(trend_data),
                          now=now)

@main.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('You do not have access to this page.')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    diseases = Disease.query.all()
    locations = Location.query.all()
    cases = Case.query.all()
    alerts = Alert.query.all()
    env_data = EnvironmentalData.query.all()
    
    return render_template('admin.html', 
                          users=users, 
                          diseases=diseases,
                          locations=locations,
                          cases=cases,
                          alerts=alerts,
                          env_data=env_data)

@main.route('/admin/add_disease', methods=['POST'])
@login_required
def add_disease():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    name = request.form.get('name')
    symptoms = request.form.get('symptoms')
    
    if not name:
        return jsonify({'success': False, 'message': 'Disease name is required'}), 400
    
    new_disease = Disease(name=name, symptoms=symptoms)
    db.session.add(new_disease)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Disease added successfully',
        'disease': {'id': new_disease.id, 'name': new_disease.name}
    })
    
@main.route('/admin/add_location', methods=['POST'])
@login_required
def add_location():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    name = request.form.get('name')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    
    if not name or not latitude or not longitude:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    new_location = Location(name=name, latitude=latitude, longitude=longitude)
    db.session.add(new_location)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Location added successfully',
        'location': {
            'id': new_location.id, 
            'name': new_location.name,
            'latitude': new_location.latitude,
            'longitude': new_location.longitude
        }
    })
    
@main.route('/admin/create_alert', methods=['POST'])
@login_required
def create_alert():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    message = request.form.get('message')
    severity = request.form.get('severity')
    location_id = request.form.get('location_id')
    
    if not message or not severity or not location_id:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    new_alert = Alert(
        message=message,
        severity=severity,
        location_id=location_id,
        created_by=current_user.id
    )
    db.session.add(new_alert)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Alert created successfully'
    })

@main.route('/sms-alerts')
@login_required
def sms_alerts():
    if current_user.role != 'admin':
        flash('You do not have access to this page.')
        return redirect(url_for('main.dashboard'))
    
    # Get locations and diseases for the form
    locations = Location.query.all()
    diseases = Disease.query.all()
    
    # Get SMS history from database with explicit join conditions
    sms_history = db.session.query(
        SMSHistory.id,
        SMSHistory.message,
        SMSHistory.alert_type,
        SMSHistory.status,
        SMSHistory.sent_at,
        Recipient.name.label('recipient_name'),
        Recipient.phone_number,
        Location.name.label('location_name')
    ).join(
        Recipient, SMSHistory.recipient_id == Recipient.id
    ).join(
        Location, Recipient.location_id == Location.id
    ).order_by(SMSHistory.sent_at.desc()).limit(50).all()
    
    # Get statistics
    total_sent = SMSHistory.query.count()
    delivered = SMSHistory.query.filter_by(status='delivered').count()
    total_recipients = Recipient.query.filter_by(is_active=True).count()
    active_alerts = Alert.query.count()
    
    stats = {
        'total_sent': total_sent,
        'delivered': delivered,
        'recipients': total_recipients,
        'active_alerts': active_alerts
    }
    
    return render_template('sms_alerts.html', 
                         locations=locations,
                         diseases=diseases,
                         sms_history=sms_history,
                         stats=stats)

@main.route('/send-sms-alert', methods=['POST'])
@login_required
def send_sms_alert():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    alert_type = request.form.get('alert_type')
    location_id = request.form.get('location_id')
    sms_message = request.form.get('message')
    disease_id = request.form.get('disease_id')
    
    if not sms_message or not location_id or not alert_type:
        flash('All fields are required.', 'error')
        return redirect(url_for('main.sms_alerts'))
    
    try:
        # Get recipients from database based on location
        if location_id == 'all':
            recipients = Recipient.query.filter_by(is_active=True).all()
            location_name = 'All Villages'
        else:
            recipients = Recipient.query.filter_by(
                location_id=int(location_id), 
                is_active=True
            ).all()
            location = Location.query.get(location_id)
            location_name = location.name if location else 'Unknown'
        
        if not recipients:
            flash('No recipients found for the selected location.', 'warning')
            return redirect(url_for('main.sms_alerts'))
        
        # Check if Twilio is available
        print(f"🔍 DEBUG: TWILIO_AVAILABLE = {TWILIO_AVAILABLE}")
        if not TWILIO_AVAILABLE:
            print("❌ Twilio check failed - showing error message")
            flash('⚠️ SMS service not configured. Please install Twilio: pip install twilio', 'error')
            return redirect(url_for('main.sms_alerts'))
        
        print("✅ Twilio check passed - proceeding to send SMS")
        
        # Twilio SMS Integration - Load credentials from environment variables
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        messaging_service_sid = os.environ.get('TWILIO_MESSAGING_SERVICE_SID')
        
        if not all([account_sid, auth_token, messaging_service_sid]):
            flash('⚠️ Twilio credentials not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_MESSAGING_SERVICE_SID in your .env file.', 'error')
            return redirect(url_for('main.sms_alerts'))
        
        client = Client(account_sid, auth_token)
        
        # Send SMS to each recipient
        sent_count = 0
        failed_count = 0
        
        for recipient in recipients:
            try:
                message = client.messages.create(
                    messaging_service_sid=messaging_service_sid,
                    body=sms_message,
                    to=recipient.phone_number
                )
                
                # Save to SMS history
                sms_history = SMSHistory(
                    recipient_id=recipient.id,
                    message=sms_message,
                    alert_type=alert_type,
                    status='sent',
                    sent_by=current_user.id,
                    twilio_sid=message.sid
                )
                db.session.add(sms_history)
                
                print(f"✅ SMS sent to {recipient.name} ({recipient.phone_number}): {message.sid}")
                sent_count += 1
                
            except Exception as sms_error:
                print(f"❌ Error sending to {recipient.name} ({recipient.phone_number}): {str(sms_error)}")
                
                # Save failed attempt to history
                sms_history = SMSHistory(
                    recipient_id=recipient.id,
                    message=sms_message,
                    alert_type=alert_type,
                    status='failed',
                    sent_by=current_user.id
                )
                db.session.add(sms_history)
                failed_count += 1
        
        # Commit all SMS history records
        db.session.commit()
        
        if sent_count > 0:
            flash(f'✅ SMS alert sent successfully to {sent_count} recipient(s) in {location_name}!', 'success')
        if failed_count > 0:
            flash(f'⚠️ {failed_count} SMS(s) failed to send.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error sending SMS: {str(e)}', 'error')
    
    return redirect(url_for('main.sms_alerts'))
