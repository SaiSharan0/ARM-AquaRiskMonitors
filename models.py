from . import db, bcrypt
from flask_login import UserMixin
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False) # admin, clinic, health_worker, analyst
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_date = db.Column(db.DateTime, server_default=func.now())
    symptoms = db.Column(db.Text)
    num_cases = db.Column(db.Integer, default=1)
    
    disease = db.relationship('Disease', backref=db.backref('cases', lazy=True))
    location = db.relationship('Location', backref=db.backref('cases', lazy=True))
    user = db.relationship('User', backref=db.backref('cases', lazy=True))

class EnvironmentalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=func.now())
    rainfall = db.Column(db.Float)
    turbidity = db.Column(db.Float)
    ph = db.Column(db.Float)
    temperature = db.Column(db.Float)
    
    location = db.relationship('Location', backref=db.backref('env_data', lazy=True))

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    alert_date = db.Column(db.DateTime, server_default=func.now())
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50)) # e.g., 'High', 'Medium', 'Low'
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    location = db.relationship('Location', backref=db.backref('alerts', lazy=True))
    user = db.relationship('User', backref=db.backref('alerts_created', lazy=True))

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    
    location = db.relationship('Location', backref=db.backref('recipients', lazy=True))

class SMSHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.String(50))  # outbreak, water_quality, prevention, custom
    status = db.Column(db.String(20), default='sent')  # sent, delivered, failed
    sent_at = db.Column(db.DateTime, server_default=func.now())
    sent_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    twilio_sid = db.Column(db.String(100))  # Twilio message SID for tracking
    
    recipient = db.relationship('Recipient', backref=db.backref('sms_history', lazy=True))
    user = db.relationship('User', backref=db.backref('sms_sent', lazy=True))
