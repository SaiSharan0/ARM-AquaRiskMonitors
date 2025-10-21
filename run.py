from app import create_app, db
from app.models import User, Disease, Location
import os

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database with default data."""
    db.create_all()
    print("Database initialized.")

    # Create default users if they don't exist
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@aquarisk.org',
            role='admin'
        )
        admin_user.set_password('Admin@123')
        db.session.add(admin_user)
        print("Admin user created.")
        
    if not User.query.filter_by(username='clinic').first():
        clinic_user = User(
            username='clinic',
            email='clinic@aquarisk.org',
            role='clinic'
        )
        clinic_user.set_password('Clinic@123')
        db.session.add(clinic_user)
        print("Clinic user created.")

    # Create default diseases if they don't exist
    diseases = [
        {'name': 'Cholera', 'description': 'Acute diarrheal infection caused by ingestion of contaminated food or water'},
        {'name': 'Typhoid', 'description': 'Bacterial infection caused by Salmonella typhi spread through contaminated food and water'},
        {'name': 'Hepatitis A', 'description': 'Liver infection caused by a virus spread through contaminated food and water'},
        {'name': 'Giardiasis', 'description': 'Intestinal infection caused by Giardia parasite found in soil, food, or water contaminated with feces'},
        {'name': 'Dysentery', 'description': 'Infection resulting in inflammation of the intestines, especially the colon'}
    ]
    
    for disease_data in diseases:
        if not Disease.query.filter_by(name=disease_data['name']).first():
            disease = Disease(name=disease_data['name'], description=disease_data['description'])
            db.session.add(disease)
            print(f"Added {disease_data['name']} to diseases.")
    
    # Create default locations for Northeast India if they don't exist
    locations = [
        {'name': 'Guwahati', 'latitude': 26.1445, 'longitude': 91.7362},
        {'name': 'Shillong', 'latitude': 25.5788, 'longitude': 91.8933},
        {'name': 'Imphal', 'latitude': 24.8170, 'longitude': 93.9368},
        {'name': 'Agartala', 'latitude': 23.8315, 'longitude': 91.2868},
        {'name': 'Aizawl', 'latitude': 23.7307, 'longitude': 92.7173}
    ]
    
    for location_data in locations:
        if not Location.query.filter_by(name=location_data['name']).first():
            location = Location(**location_data)
            db.session.add(location)
            print(f"Added {location_data['name']} to locations.")
            
    db.session.commit()
    print("Default data added successfully.")


@app.cli.command("create-admin")
def create_admin():
    """Create a new admin user."""
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    if User.query.filter_by(username=username).first():
        print(f"User {username} already exists.")
        return
    
    if User.query.filter_by(email=email).first():
        print(f"Email {email} already registered.")
        return
    
    user = User(username=username, email=email, role='admin')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Admin user {username} created successfully.")

@app.cli.command("reset-password")
def reset_password():
    """Reset a user's password."""
    username = input("Enter username: ")
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"User {username} not found.")
        return
    
    new_password = input("Enter new password: ")
    user.set_password(new_password)
    db.session.commit()
    print(f"Password for {username} has been reset.")

if __name__ == '__main__':
    # Set host to 0.0.0.0 to make the server externally visible
    # Set debug=False for production
    is_debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting AquaRisk Monitor on port {port}...")
    print(f"Debug mode: {'Enabled' if is_debug else 'Disabled'}")
    print(f"Access the application at: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=is_debug)
