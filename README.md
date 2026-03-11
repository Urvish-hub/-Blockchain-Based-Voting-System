# Online Voting System

A secure and modern web-based voting system built with Flask and MySQL.

## Features

- **User Features:**
  - Voter registration
  - Secure login
  - Vote casting
  - View election results
  - Personal dashboard

- **Admin Features:**
  - Admin authentication
  - Add/Edit/Delete candidates
  - View registered voters
  - Monitor voting progress
  - View results

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- MySQL Server
- pip (Python package manager)

### 2. Database Setup
1. Create a MySQL database:
```sql
CREATE DATABASE voting_system;
```

2. Import the database schema:
```bash
mysql -u root -p voting_system < database/voting.sql
```

### 3. Configuration
1. Update `config.py` with your MySQL credentials:
   - Update `DB_CONFIG` with your MySQL host, user, password

2. Update `SECRET_KEY` in `config.py` for production use.

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Default Admin Credentials
- Username: `admin`
- Password: `admin123` (Change this after first login!)

## Project Structure
```
Online-Voting-System/
├── app.py                 # Main Flask application
├── config.py              # Configuration file
├── requirements.txt       # Python dependencies
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── database/              # Database schema
├── models/                # Database models
└── routes/                # Route handlers
```

## Security Notes
- Change default admin credentials
- Update SECRET_KEY for production
- Use HTTPS in production
- Implement additional security measures as needed

## License
This project is for educational purposes.

