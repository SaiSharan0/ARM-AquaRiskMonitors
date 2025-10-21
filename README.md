# AquaRisk Monitor

A Smart Community Health Monitoring and Early Warning System for water-borne diseases.

## Project Overview

AquaRisk Monitor is a comprehensive full-stack web application designed to track, monitor, and predict water-borne diseases. The platform provides health officials, clinic staff, and administrators with data-driven tools for disease surveillance, early warning, and intervention planning.

## Features

- **Secure Authentication:** Role-based access control with bcrypt password hashing (admin, clinic, field_worker)
- **Interactive Dashboard:** Real-time metrics on active cases, hotspots, and water quality parameters
- **Case Reporting System:** Structured form for clinic staff to report new disease cases with location pinning
- **Geospatial Visualization:** Interactive map showing disease hotspots, contamination zones, and case distributions
- **Trend Analysis:** Visual analytics correlating environmental factors (rainfall, turbidity, etc.) with disease outbreaks
- **Early Warning System:** Automated alerts for potential outbreaks based on environmental and case data
- **Admin Control Panel:** Comprehensive tools for managing users, diseases, locations, and system settings

## Technology Stack

- **Backend:** Python 3.x, Flask 2.3.3
- **Database:** SQLite (development) / MySQL (production)
- **Authentication:** Flask-Login with Flask-Bcrypt for secure password handling
- **Frontend:** HTML5, CSS3 with responsive design
- **Data Visualization:** Chart.js for trend analysis, Leaflet.js for interactive maps
- **Security:** Content Security Policy, CSRF protection, XSS prevention

## Setup Instructions

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd AquaRisk-Monitor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```
   
   Or use the batch file on Windows:
   ```bash
   start_aquarisk.bat
   ```
   This will:
   - Install required Python packages
   - Configure environment variables
   - Initialize the database with default data
   - Start the application server

4. **Access the application:**
   Open a web browser and navigate to `http://localhost:5000`

5. **Default login credentials:**
   - Admin: 
     - Email: admin@aquarisk.org
     - Password: Admin@123
   - Clinic Staff:
     - Email: clinic@aquarisk.org
     - Password: Clinic@123

## Project Structure

```
AquaRisk-Monitor/
├── app/                      # Application package
│   ├── __init__.py           # Application factory and configuration
│   ├── models.py             # Database models
│   ├── routes.py             # Route handlers
│   ├── static/               # Static files
│   │   ├── css/              # CSS stylesheets
│   │   │   └── style.css     # Main stylesheet
│   │   └── images/           # Image assets
│   └── templates/            # HTML templates
│       ├── admin.html        # Admin dashboard
│       ├── base.html         # Base template with layout
│       ├── dashboard.html    # Main dashboard
│       ├── index.html        # Landing page
│       ├── login.html        # Authentication
│       ├── map_view.html     # Interactive map
│       ├── register.html     # User registration
│       ├── report.html       # Case reporting form
│       └── trends.html       # Data analysis
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
├── schema.sql                # Database schema
├── start_aquarisk.bat        # Setup and run script
└── README.md                 # Documentation
```

## Development Commands

- **Initialize database with sample data:**
  ```bash
  flask init-db
  ```

- **Create a new admin user:**
  ```bash
  flask create-admin
  ```

- **Reset a user's password:**
  ```bash
  flask reset-password
  ```

## Security Measures

- **Password Security:** All passwords are hashed with bcrypt
- **Input Validation:** Form validation for all user inputs
- **CSRF Protection:** Cross-Site Request Forgery protection on forms
- **Content Security Policy:** Restrictions on script sources
- **HTTP Security Headers:** Protection against XSS and clickjacking

## Machine Learning Integration

The system incorporates predictive analytics for early warning and risk assessment:

- **Input Data:** Historical case data, environmental data (rainfall, water quality), and population density
- **Model:** Predictive models for risk assessment and hotspot identification
- **Integration:** Automated data processing pipeline for continuous monitoring
- **Output:**
  - **Hotspots:** Geographic coordinates of areas with high predicted disease incidence
  - **Risk Assessment:** Categorical ratings (High, Medium, Low) for different regions

## Future Enhancements

1. **Mobile Application:** Companion mobile app for field workers
2. **SMS Alerts:** Integration with SMS services for alerts in areas with limited internet
3. **Advanced Predictive Analytics:** Enhanced machine learning model for outbreak prediction
4. **Offline Support:** Progressive Web App functionality for offline use
5. **API Integration:** Connection with weather and water quality monitoring services

---

© 2025 AquaRisk Monitor | Smart Community Health Monitoring and Early Warning System

