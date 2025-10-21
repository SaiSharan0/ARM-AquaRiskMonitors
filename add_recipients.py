from app import create_app, db
from app.models import Location, Recipient

app = create_app()

with app.app_context():
    # Clear existing recipients
    Recipient.query.delete()
    db.session.commit()
    print("Cleared existing recipients.")
    
    # Get all locations
    locations = Location.query.all()
    
    if not locations:
        print("No locations found! Please run reset_data.py first.")
        exit()
    
    # Sample phone numbers (you can replace these with real numbers)
    # Format: +91XXXXXXXXXX for India
    sample_numbers = [
        '+919000920167',  # Your test number
        '+919876543210',
        '+919876543211',
        '+919876543212',
        '+919876543213',
        '+919876543214',
        '+919876543215',
        '+919876543216',
        '+919876543217',
        '+919876543218'
    ]
    
    # Add 10 recipients for each location
    recipient_count = 0
    for location in locations:
        for i in range(10):
            # Rotate through sample numbers
            phone_number = sample_numbers[i % len(sample_numbers)]
            
            recipient = Recipient(
                name=f"Villager {i+1} - {location.name}",
                phone_number=phone_number,
                location_id=location.id,
                is_active=True
            )
            db.session.add(recipient)
            recipient_count += 1
    
    db.session.commit()
    print(f"\n✅ Successfully added {recipient_count} recipients across {len(locations)} locations!")
    
    # Show summary
    print("\n📊 Summary by Location:")
    for location in locations:
        count = Recipient.query.filter_by(location_id=location.id).count()
        print(f"  - {location.name}: {count} recipients")
    
    print("\n💡 Note: Update phone numbers in this script with real numbers before production use!")
    print("   Current phone numbers are samples and will repeat across locations.")
