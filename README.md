# Smart PG Management System

A comprehensive web-based application designed to manage PG and hostel operations efficiently. This system handles everything from room allotments and bookings to complaint resolution and resident history.

## Table of Contents
1. Core Features
2. Technology Stack
3. Project Structure
4. Installation and Setup
5. User Roles and Access
6. Database Schema
7. Automated Testing

## Core Features

### For Residents
- Search for available rooms by sharing type.
- Real-time room booking with move-in date selection.
- Personal dashboard to view active stay details.
- Stay history tracking showing previous room allotments.
- Complaint submission portal with status tracking.
- Monthly rent payment status overview.

### For Admin (Warden)
- High-level overview of total revenue and resident statistics.
- Management of all active residents and their booking statuses.
- Real-time room capacity management (Automatic bed release on vacate/kick out).
- Complaint management system to track and resolve resident issues.
- Role-based authorization and secure login.

## Technology Stack
- Backend: Python 3 with Flask Framework
- Database: SQLite3 (Relational database management)
- Frontend: Vanilla HTML5, CSS3 (Modular design system), and JavaScript
- Authentication: Secure password hashing using SHA-256
- Testing: Automated UI testing with Selenium WebDriver

## Installation and Setup

### Prerequisites
- Python 3.x installed
- pip (Python package manager)
- Google Chrome (for automated testing features)

### Step 1: Clone the Repository
Clone this folder to your local machine to get started.

### Step 2: Install Dependencies
Run the following command to install required Python libraries:
pip install -r requirements.txt

### Step 3: Initialize the Database
Run the setup script to create tables and populate them with realistic initial data:
python3 init_db.py

### Step 4: Run the Application
Start the Flask development server:
python3 app.py

The application will be accessible at: http://127.0.0.1:5001

## User Roles and Access

### Admin Access
- Username: admin@example.com
- Password: admin123
- Permissions: Full control over residents, rooms, and complaints.

### Resident Access
- Test Account: ananya@example.com
- Password: password123
- Permissions: Limited to personal stay details, bookings, and complaints.

## Project Structure
- app.py: Main application logic and routing.
- init_db.py: Database initialization and data population script.
- templates/: HTML structure for all pages.
- static/css/: Custom styling and layout system.
- test_app.py: Automated selenium test suite.

## Automated Testing
The project includes a dedicated testing script to verify all core functionalities. To run the tests:
python3 test_app.py

This script verifies login flows, complaint submissions, and admin status updates automatically.
