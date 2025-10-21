import os
from urllib.parse import quote_plus
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)

    # Configuration with enhanced security
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # MySQL Database Configuration from environment variables
    db_user = os.environ.get('DB_USER', 'root')
    db_password = quote_plus(os.environ.get('DB_PASSWORD', ''))
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME', 'aquarisk_db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
    
    print(f"✅ Using MySQL database: {db_name}")
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Allow required CDNs and map tiles while keeping a strict baseline
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://code.jquery.com https://cdn.datatables.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://fonts.googleapis.com https://cdn.datatables.net; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data: https://*.tile.openstreetmap.org https://*.tile.openstreetmap.fr https://unpkg.com https://raw.githubusercontent.com https://img.icons8.com; "
            "connect-src 'self' https://cdn.jsdelivr.net https://unpkg.com https://nominatim.openstreetmap.org; "
            "frame-ancestors 'none'"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        print(f"CSP SET: img-src includes unpkg.com: {'unpkg.com' in csp_policy}")
        return response

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'

    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Register custom filters
    from .filters import filters_blueprint
    app.register_blueprint(filters_blueprint)

    # User loader callback
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Inject current datetime into all templates
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.now()}

    # Create database tables and default data
    with app.app_context():
        db.create_all()
        create_default_data()

    return app

def create_default_data():
    """Create default data if it doesn't exist"""
    from .models import User, Disease, Location, Case, EnvironmentalData, Alert
    
    # Create default admin user if it doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@aquarisk.org',
            role='admin'
        )
        # Get password from environment variable
        admin_password = os.environ.get('ADMIN_PASSWORD', 'ChangeMe@123')
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
    
    # Create default clinic user if it doesn't exist
    clinic_user = User.query.filter_by(username='clinic').first()
    if not clinic_user:
        clinic_user = User(
            username='clinic',
            email='clinic@aquarisk.org',
            role='clinic'
        )
        # Get password from environment variable
        clinic_password = os.environ.get('CLINIC_PASSWORD', 'ChangeMe@123')
        clinic_user.set_password(clinic_password)
        db.session.add(clinic_user)
    
    # Create default diseases if they don't exist
    diseases = [
        {'name': 'Cholera', 'description': 'Acute diarrheal infection caused by ingestion of contaminated food or water'},
        {'name': 'Typhoid', 'description': 'Bacterial infection caused by Salmonella typhi spread through contaminated food and water'},
        {'name': 'Hepatitis A', 'description': 'Liver infection caused by a virus spread through contaminated food and water'},
        {'name': 'Giardiasis', 'description': 'Intestinal infection caused by Giardia parasite found in soil, food, or water contaminated with feces'}
    ]
    
    for disease_data in diseases:
        disease = Disease.query.filter_by(name=disease_data['name']).first()
        if not disease:
            disease = Disease(name=disease_data['name'], description=disease_data['description'])
            db.session.add(disease)
    
    # Create default locations if they don't exist
    locations = [
        {'name': 'Chennai', 'latitude': 13.0827, 'longitude': 80.2707},
        {'name': 'Mumbai', 'latitude': 19.0760, 'longitude': 72.8777},
        {'name': 'Delhi', 'latitude': 28.7041, 'longitude': 77.1025},
        {'name': 'Kolkata', 'latitude': 22.5726, 'longitude': 88.3639},
        {'name': 'Bangalore', 'latitude': 12.9716, 'longitude': 77.5946}
    ]
    
    for location_data in locations:
        location = Location.query.filter_by(name=location_data['name']).first()
        if not location:
            location = Location(
                name=location_data['name'],
                latitude=location_data['latitude'],
                longitude=location_data['longitude']
            )
            db.session.add(location)
    
    db.session.commit()
    
    # Add some sample cases and environmental data
    if Case.query.count() == 0:
        # Add sample cases if there are none
        admin = User.query.filter_by(username='admin').first()
        cholera = Disease.query.filter_by(name='Cholera').first()
        typhoid = Disease.query.filter_by(name='Typhoid').first()
        locations = Location.query.all()
        
        if admin and cholera and typhoid and locations:
            # Add cases to different locations
            for i, location in enumerate(locations):
                # Add cholera cases
                case1 = Case(
                    disease_id=cholera.id,
                    location_id=location.id,
                    user_id=admin.id,
                    symptoms="Diarrhea, vomiting, leg cramps",
                    num_cases=5 + i * 3  # Varying number of cases
                )
                db.session.add(case1)
                
                # Add typhoid cases
                case2 = Case(
                    disease_id=typhoid.id,
                    location_id=location.id,
                    user_id=admin.id,
                    symptoms="High fever, weakness, stomach pain, headache",
                    num_cases=3 + i * 2  # Varying number of cases
                )
                db.session.add(case2)
                
                # Add environmental data
                env_data = EnvironmentalData(
                    location_id=location.id,
                    rainfall=75.5 + i * 10,
                    turbidity=3.2 + i * 0.5,
                    ph=6.8 + i * 0.2,
                    temperature=28.5 + i * 1.5
                )
                db.session.add(env_data)
                
                # Add alert for locations with high case numbers
                if i >= 2:
                    alert = Alert(
                        location_id=location.id,
                        message=f"High number of waterborne disease cases detected in {location.name}",
                        severity="High" if i > 3 else "Medium",
                        created_by=admin.id
                    )
                    db.session.add(alert)
    
    db.session.commit()
