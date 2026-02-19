# SHEild-X
Women's safety navigation app with risk-based safe routing .

## Problem Statement

In India, 51% of women report feeling unsafe while traveling alone, with 95% stating that safety concerns affect their mobility choices (Source: ActionAid Survey). Traditional navigation applications like Google Maps optimize for distance or time, completely disregarding safety parameters that matter most to women travelers.

**The Problem:**
- Women often avoid well-lit main roads at night due to lack of information about safer alternatives
- GPS applications suggest shortcuts through isolated lanes without warning about potential risks
- No integration of crime statistics or accident data in route planning
- Emergency services are multiple clicks away during crisis situations
- Lack of community feedback on route safety

**The Impact:**
- Restricted mobility and independence for women
- Limited career and education opportunities due to travel fears
- Anxiety and stress during everyday commutes
- Delayed emergency response in crisis situations

---

### How We Have Implemented SHEild-X

**1. Road Network Extraction**
We use OpenStreetMap data accessed through the OSMnx library to download real road networks. For demonstration purposes, we have focused on Coimbatore, India, extracting all drivable roads, intersections, and road attributes.

**2. Risk Assignment Based on Road Type**
Each road segment is assigned a base risk score according to its classification:
- Primary roads and highways: Low risk (0.2)
- Residential roads: Medium risk (0.5)
- Service roads and alleys: High risk (0.7)

**3. Simulated Incident Data**
Since real government incident data requires API access, we have created sample incident data for Coimbatore locations including Gandhipuram, RS Puram, and Town Hall. Each incident has a severity score (0.4 to 0.9) that adds risk to nearby roads.

**4. Time-Dependent Risk Adjustment**
The system checks the current time and applies risk multipliers:
- Night hours (after 9 PM): Risk increased by 1.4x
- This simulates how darkness and reduced crowd affect safety

**5. Risk Propagation**
Risk spreads to neighboring roads through graph diffusion, ensuring that areas near high-risk zones are also appropriately weighted.

**6. Path Finding Algorithm**
We use NetworkX's shortest path implementation with a custom weight function:
Total Cost = (0.7 × Risk) + (0.3 × Distance)

text
This prioritizes safety while still considering reasonable travel distance.

**7. Safe Haven Integration**
Police stations and hospitals are extracted from OpenStreetMap and displayed as markers on the map. Routes can be adjusted to stay near these safe locations.

**8. Interactive Frontend**
The application features:
- A React-based user interface
- Leaflet map integration showing roads and routes
- Search functionality for locations
- Visual display of the safest route in red
- Distance and estimated time display
- SOS emergency button for one-click calling to police (100)

### Current Limitations
- Users must manually download a city before exploring
- Incident data is simulated rather than from government sources
- No user rating system implemented yet
- Voice guidance not currently available

Our current implementation demonstrates the core concept of safety-first routing, providing a foundation for future enhancements with real data sources and community features.


## Technology Stack

Backend
- Python - Core programming language
- Flask - Web server and API framework
- OSMnx - OpenStreetMap data extraction
- NetworkX - Graph algorithms for path finding
- NumPy - Mathematical calculations

Frontend
- React - User interface framework
- Leaflet - Interactive maps
- Axios - API communication
- React Icons - UI icons

Data Source
- OpenStreetMap - Free and open map data

Emergency Feature
- Native tel: protocol for one-click emergency calling

---

## Future Enhancements

### Infinite Map Loading
Currently, users need to manually download a city before exploring. We are working on infinite map scrolling - simply pan and zoom to any location, and the road network loads automatically in the background. This will eliminate manual download buttons for seamless exploration.

### Real Government Data Integration
Our current prototype uses sample incident data for demonstration. We plan to integrate with official government sources:
- iRAD (Integrated Road Accident Database) - Real accident statistics from Ministry of Road Transport
- Crime Bureau APIs - Historical crime data by location
- Traffic Police Feeds - Real-time incident reports

This will replace simulated data with authentic, verifiable safety intelligence.

### Community Rating System
After each journey, users will be able to:
- Rate the route safety on a 1-5 star scale
- Report specific concerns such as poor lighting, suspicious activity, or accidents
- Share photos or descriptions of unsafe conditions

This crowd-sourced data creates a living safety map that improves with every user interaction. Routes with consistently poor ratings will be automatically deprioritized.

### Voice Guidance and Alerts
Turn-by-turn voice instructions will announce:
- Upcoming turns with road names
- "Safe zone ahead" alerts when approaching police stations
- "Caution: poorly lit area" warnings
- "Hospital nearby" notifications
- Real-time rerouting if incidents are reported ahead

### Community-Driven Safety Network
Every user becomes a safety contributor. Ratings, reports, and feedback help other women travel safer. Together, we build a crowd-powered safety layer over traditional maps.

These enhancements will transform SHEild-X from a navigation application into a community-driven safety ecosystem for women.

---

## Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- Git

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/SHEild-X.git
cd SHEild-X

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Start backend server
python backend/app.py
