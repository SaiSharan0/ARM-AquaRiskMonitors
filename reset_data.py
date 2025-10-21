"""
Script to reset database with North East India village data
"""
from app import create_app, db
from app.models import Case, Disease, Location, User, Alert, EnvironmentalData
from datetime import datetime, timedelta
import random

def reset_database():
    app = create_app()
    with app.app_context():
        print("🗑️  Clearing existing data...")
        
        # Delete all existing data (except users)
        Case.query.delete()
        Alert.query.delete()
        EnvironmentalData.query.delete()
        Location.query.delete()
        Disease.query.delete()
        
        db.session.commit()
        print("✅ Existing data cleared!")
        
        print("\n📋 Creating diseases...")
        # Create waterborne diseases common in North East India
        diseases_data = [
            {'name': 'Cholera', 'description': 'Acute diarrheal disease caused by contaminated water'},
            {'name': 'Typhoid', 'description': 'Bacterial infection from contaminated food/water'},
            {'name': 'Hepatitis A', 'description': 'Liver infection from contaminated water'},
            {'name': 'Diarrhea', 'description': 'Loose, watery bowel movements from contaminated water'},
            {'name': 'Dysentery', 'description': 'Intestinal infection causing bloody diarrhea'},
            {'name': 'Giardiasis', 'description': 'Intestinal parasitic infection from water'},
        ]
        
        diseases = []
        for d in diseases_data:
            disease = Disease(name=d['name'], description=d['description'])
            db.session.add(disease)
            diseases.append(disease)
        
        db.session.commit()
        print(f"✅ Created {len(diseases)} diseases")
        
        print("\n📍 Creating North East India village locations...")
        # North East India villages with real coordinates
        locations_data = [
            # Assam
            {'name': 'Majuli Island', 'state': 'Assam', 'lat': 26.9501, 'lng': 94.2155},
            {'name': 'Kaziranga Village', 'state': 'Assam', 'lat': 26.5775, 'lng': 93.1711},
            {'name': 'Sivasagar Town', 'state': 'Assam', 'lat': 26.9845, 'lng': 94.6382},
            {'name': 'Tezpur Village', 'state': 'Assam', 'lat': 26.6338, 'lng': 92.8000},
            {'name': 'Jorhat Rural', 'state': 'Assam', 'lat': 26.7509, 'lng': 94.2037},
            
            # Meghalaya
            {'name': 'Cherrapunji Village', 'state': 'Meghalaya', 'lat': 25.2691, 'lng': 91.7319},
            {'name': 'Mawlynnong Village', 'state': 'Meghalaya', 'lat': 25.1881, 'lng': 91.9421},
            {'name': 'Shillong Outskirts', 'state': 'Meghalaya', 'lat': 25.5788, 'lng': 91.8933},
            {'name': 'Nongstoin Village', 'state': 'Meghalaya', 'lat': 25.5167, 'lng': 91.2667},
            
            # Arunachal Pradesh
            {'name': 'Ziro Valley', 'state': 'Arunachal Pradesh', 'lat': 27.5442, 'lng': 93.8315},
            {'name': 'Tawang Village', 'state': 'Arunachal Pradesh', 'lat': 27.5860, 'lng': 91.8590},
            {'name': 'Pasighat Town', 'state': 'Arunachal Pradesh', 'lat': 28.0660, 'lng': 95.3265},
            
            # Manipur
            {'name': 'Imphal Rural', 'state': 'Manipur', 'lat': 24.8170, 'lng': 93.9368},
            {'name': 'Moirang Village', 'state': 'Manipur', 'lat': 24.4969, 'lng': 93.7718},
            {'name': 'Ukhrul Village', 'state': 'Manipur', 'lat': 25.0535, 'lng': 94.3574},
            
            # Nagaland
            {'name': 'Kohima Village', 'state': 'Nagaland', 'lat': 25.6747, 'lng': 94.1079},
            {'name': 'Dimapur Rural', 'state': 'Nagaland', 'lat': 25.9039, 'lng': 93.7291},
            {'name': 'Mokokchung Village', 'state': 'Nagaland', 'lat': 26.3224, 'lng': 94.5244},
            
            # Tripura
            {'name': 'Agartala Outskirts', 'state': 'Tripura', 'lat': 23.8315, 'lng': 91.2868},
            {'name': 'Udaipur Village', 'state': 'Tripura', 'lat': 23.5333, 'lng': 91.4833},
            
            # Mizoram
            {'name': 'Aizawl Rural', 'state': 'Mizoram', 'lat': 23.7271, 'lng': 92.7176},
            {'name': 'Champhai Village', 'state': 'Mizoram', 'lat': 23.4714, 'lng': 93.3268},
            
            # Sikkim
            {'name': 'Gangtok Outskirts', 'state': 'Sikkim', 'lat': 27.3389, 'lng': 88.6065},
            {'name': 'Namchi Village', 'state': 'Sikkim', 'lat': 27.1649, 'lng': 88.3641},
            {'name': 'Pelling Village', 'state': 'Sikkim', 'lat': 27.3161, 'lng': 88.2186},
        ]
        
        locations = []
        for l in locations_data:
            location = Location(
                name=l['name'],
                latitude=l['lat'],
                longitude=l['lng']
            )
            db.session.add(location)
            locations.append(location)
        
        db.session.commit()
        print(f"✅ Created {len(locations)} village locations")
        
        print("\n💉 Creating disease cases...")
        # Get admin user for case reporting
        admin_user = User.query.filter_by(email='admin@aquarisk.org').first()
        if not admin_user:
            print("⚠️  Warning: Admin user not found. Creating admin user...")
            admin_user = User(
                username='admin',
                email='admin@aquarisk.org',
                role='admin'
            )
            admin_user.set_password('Admin@123')
            db.session.add(admin_user)
            db.session.commit()
        
        # Create cases for different villages
        cases_created = 0
        base_date = datetime.now()
        
        for location in locations:
            # Each location gets 1-3 different disease cases
            num_diseases = random.randint(1, 3)
            selected_diseases = random.sample(diseases, num_diseases)
            
            for disease in selected_diseases:
                # Number of cases varies by severity
                if disease.name in ['Cholera', 'Typhoid']:
                    num_cases = random.randint(15, 35)  # High risk
                elif disease.name in ['Hepatitis A', 'Dysentery']:
                    num_cases = random.randint(8, 18)   # Medium risk
                else:
                    num_cases = random.randint(2, 8)    # Low risk
                
                # Random date within last 30 days
                days_ago = random.randint(1, 30)
                case_date = base_date - timedelta(days=days_ago)
                
                case = Case(
                    disease_id=disease.id,
                    location_id=location.id,
                    user_id=admin_user.id,
                    num_cases=num_cases,
                    case_date=case_date,
                    symptoms=f'Reported cases of {disease.name} in {location.name}'
                )
                db.session.add(case)
                cases_created += 1
        
        db.session.commit()
        print(f"✅ Created {cases_created} disease cases")
        
        print("\n🌊 Creating environmental data...")
        # Add water quality data for some locations
        env_data_created = 0
        for location in random.sample(locations, min(15, len(locations))):
            env_data = EnvironmentalData(
                location_id=location.id,
                timestamp=datetime.now() - timedelta(days=random.randint(1, 10)),
                rainfall=random.uniform(50.0, 300.0),
                ph=random.uniform(6.5, 8.5),
                turbidity=random.uniform(2.0, 25.0),
                temperature=random.uniform(18.0, 28.0)
            )
            db.session.add(env_data)
            env_data_created += 1
        
        db.session.commit()
        print(f"✅ Created {env_data_created} environmental data entries")
        
        print("\n" + "="*50)
        print("✅ Database reset complete!")
        print("="*50)
        print(f"\n📊 Summary:")
        print(f"   • {len(diseases)} diseases")
        print(f"   • {len(locations)} village locations (North East India)")
        print(f"   • {cases_created} disease cases")
        print(f"   • {env_data_created} environmental data entries")
        print(f"\n🔐 Admin credentials remain unchanged:")
        print(f"   Email: admin@aquarisk.org")
        print(f"   Password: Admin@123")
        print("\n✨ Refresh your browser to see the new data!")

if __name__ == '__main__':
    reset_database()
