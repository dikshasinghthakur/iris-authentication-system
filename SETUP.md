# 🔐 Iris Authentication System - Complete Setup Guide

## Table of Contents
1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Features](#features)
6. [Database Structure](#database-structure)
7. [API Endpoints](#api-endpoints)
8. [GUI Usage](#gui-usage)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The **Iris Authentication System** is a complete biometric identification platform featuring:
- ✅ Iris enrollment with real-time camera capture
- ✅ 1:1 verification (known user authentication)
- ✅ 1:N identification (unknown user search)
- ✅ Desktop GUI with visualizations
- ✅ REST API backend
- ✅ SQLite database with detailed logging
- ✅ Advanced iris image processing
- ✅ Multi-metric similarity matching
- ✅ Analytics and statistics dashboard

---

## System Requirements

### Hardware
- **Processor**: Intel i5 or equivalent (2.0 GHz+)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB free space
- **Camera**: Webcam with 640×480+ resolution

### Software (Windows/Mac/Linux)
- **Python**: 3.8 or higher
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Git**: Optional, for version control

---

## Installation

### Step 1: Install Python
**Windows**: Download from https://www.python.org/downloads/
- ✅ Check "Add Python to PATH"
- ✅ Run installer

**Mac**: Using Homebrew
```bash
brew install python3
```

**Linux**:
```bash
sudo apt-get install python3 python3-pip python3-venv
```

### Step 2: Download/Clone Project
```bash
# Navigate to Desktop
cd "Desktop"

# Or clone if using git
git clone <repository-url> "iris system with password"
cd "iris system with password"
```

### Step 3: Install Dependencies
```bash
# Windows
pip install -r requirements.txt

# Mac/Linux
pip3 install -r requirements.txt
```

### Step 4: Verify Installation
```bash
# Check Flask
python -c "import flask; print(flask.__version__)"

# Check OpenCV
python -c "import cv2; print(cv2.__version__)"

# Check Database
python -c "import sqlite3; print(sqlite3.version)"
```

---

## Quick Start

### Option A: GUI Application (Recommended)

**Windows**:
```bash
# Navigate to project directory
cd "C:\Users\hp\OneDrive\Desktop\iris system with password"

# Run startup script
start_windows.bat
```

**Mac/Linux**:
```bash
cd ~/Desktop/"iris system with password"
chmod +x start.sh
./start.sh
```

### Option B: Manual Start

**Terminal 1 - Backend**:
```bash
cd backend
python app.py
# Expected output: Running on http://127.0.0.1:5000
```

**Terminal 2 - GUI**:
```bash
cd gui
python gui.py
```

---

## Features

### 1. 📝 Enrollment
- Capture iris image via webcam
- Real-time preview with center guide
- Automatic iris feature extraction (152 features)
- User metadata storage

**Process**:
1. Enter username and email
2. Click "Start Camera"
3. Position eye in center guide
4. Click "Capture"
5. Click "Enroll User"

### 2. 🔑 Verification (1:1 Matching)
- Authenticate known user
- Compare against stored template
- Real-time confidence scoring
- Access grant/deny decision

**Decision Logic**:
- Similarity Score ≥ 0.65 → Access Granted ✓
- Similarity Score < 0.65 → Access Denied ✗

### 3. 🔍 Identification (1:N Matching)
- Identify user without prior ID
- Search entire database
- Show top matches with confidence
- Best match determination

**Decision Logic**:
- Best Score ≥ 0.60 → User Identified ✓
- Best Score < 0.60 → Unknown User ✗

### 4. 👥 User Management
- View all enrolled users
- Display user statistics
- View access history
- Delete users

### 5. 📊 Analytics Dashboard
- Real-time statistics
- Success rate graphs
- Activity breakdown pie charts
- Performance metrics

---

## Database Structure

### SQLite Tables

#### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    iris_template BLOB,
    enrollment_date TIMESTAMP,
    last_access TIMESTAMP,
    access_count INTEGER,
    status TEXT
);
```

#### Authentication Logs Table
```sql
CREATE TABLE auth_logs (
    log_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT,
    similarity_score REAL,
    success BOOLEAN,
    timestamp TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### System Metrics Table
```sql
CREATE TABLE system_metrics (
    metric_id INTEGER PRIMARY KEY,
    action_type TEXT,
    processing_time REAL,
    feature_count INTEGER,
    quality_score REAL,
    timestamp TIMESTAMP
);
```

#### Identification Logs Table
```sql
CREATE TABLE identification_logs (
    id_log_id INTEGER PRIMARY KEY,
    identified_user_id INTEGER,
    similarity_score REAL,
    search_time REAL,
    candidates_searched INTEGER,
    success BOOLEAN,
    timestamp TIMESTAMP,
    FOREIGN KEY (identified_user_id) REFERENCES users(user_id)
);
```

---

## API Endpoints

### Base URL
```
http://localhost:5000
```

### 1. Health Check
**Endpoint**: `GET /health`
```json
Response:
{
    "status": "healthy",
    "enrolled_users": 3,
    "timestamp": "2024-01-15T10:30:00"
}
```

### 2. Enrollment
**Endpoint**: `POST /enroll`
```json
Request:
{
    "username": "alice_smith",
    "email": "alice@example.com",
    "image": "base64_encoded_image"
}

Response:
{
    "success": true,
    "user_id": 1,
    "message": "User alice_smith enrolled successfully",
    "features_extracted": 152
}
```

### 3. Verification (1:1)
**Endpoint**: `POST /verify`
```json
Request:
{
    "username": "alice_smith",
    "image": "base64_encoded_image"
}

Response:
{
    "success": true,
    "similarity": 0.8230,
    "threshold": 0.65,
    "message": "Authentication successful"
}
```

### 4. Identification (1:N)
**Endpoint**: `POST /identify`
```json
Request:
{
    "image": "base64_encoded_image"
}

Response:
{
    "success": true,
    "best_match": {
        "user_id": 2,
        "username": "bob_jones",
        "email": "bob@example.com",
        "similarity": 0.8145
    },
    "all_matches": [...],
    "threshold": 0.60
}
```

### 5. Get Users
**Endpoint**: `GET /users`
```json
Response:
{
    "users": [
        {
            "user_id": 1,
            "username": "alice_smith",
            "email": "alice@example.com",
            "enrollment_date": "2024-01-15",
            "access_count": 5,
            "status": "active"
        }
    ],
    "total": 3
}
```

### 6. Get User Details
**Endpoint**: `GET /user/<id>`
```json
Response:
{
    "user_id": 1,
    "username": "alice_smith",
    "email": "alice@example.com",
    "enrollment_date": "2024-01-15",
    "access_count": 5,
    "recent_logs": [...]
}
```

### 7. Delete User
**Endpoint**: `DELETE /delete/<id>`
```json
Response:
{
    "success": true,
    "message": "User alice_smith deleted successfully"
}
```

### 8. Get Logs
**Endpoint**: `GET /logs`
```json
Response:
{
    "logs": [...],
    "metrics": [...],
    "total_logs": 45
}
```

### 9. Statistics
**Endpoint**: `GET /stats`
```json
Response:
{
    "total_users": 3,
    "total_authentications": 25,
    "successful_authentications": 23,
    "authentication_success_rate": 92.0,
    "total_identifications": 10,
    "successful_identifications": 9,
    "identification_success_rate": 90.0,
    "average_similarity": 0.7845
}
```

---

## GUI Usage

### Main Interface
The GUI has 5 tabs:

#### 1. 📝 Enroll Tab
- Left: Live camera feed
- Right: User information form
- **Steps**:
  1. Enter username and email
  2. Click "Start Camera"
  3. Position eye in center guide
  4. Click "Capture"
  5. Click "Enroll User"

#### 2. 🔑 Verify Tab
- Left: Live camera feed
- Right: Username input & confidence display
- **Steps**:
  1. Enter username
  2. Click "Start Camera"
  3. Capture iris image
  4. Click "Verify User"
  5. Check result (✓ or ✗)

#### 3. 🔍 Identify Tab
- Left: Live camera feed
- Right: Results and top matches
- **Steps**:
  1. Click "Start Camera"
  2. Capture iris image
  3. Click "Identify"
  4. View identified user

#### 4. 👥 Manage Tab
- User list with details
- View user information
- Delete users
- Refresh list

#### 5. 📊 Analytics Tab
- Real-time statistics
- Success rate graphs
- Activity breakdown
- Performance metrics

---

## Iris Processing Pipeline

### Image Processing Steps

1. **Bilateral Filtering**
   - Reduces noise while preserving edges
   - Parameter: d=9, sigma=75

2. **CLAHE (Contrast Limited Adaptive Histogram Equalization)**
   - Enhances iris contrast
   - Parameter: clipLimit=3.0, tileGridSize=8×8

3. **Morphological Operations**
   - Closes small gaps
   - Kernel: 5×5 ellipse

4. **Normalization**
   - Rescales pixel values to 0-255
   - Prepares for feature extraction

### Feature Extraction (152 Total Features)

1. **Gabor Filters (120 features)**
   - 2 scales × 3 sigmas × 5 orientations × 2 stats
   - Captures texture and patterns

2. **Statistical Features (9)**
   - Mean, Std, Max, Min, Median
   - Percentiles, Variance

3. **Texture Features (18)**
   - 3×3 block grid analysis
   - 2 features per block (mean, std)

4. **Edge Features (5)**
   - Sobel derivatives
   - Gradient magnitude

### Similarity Matching

**Three Metrics Combined**:
- 50% Cosine Similarity (direction)
- 30% Euclidean Distance (magnitude)
- 20% Manhattan Distance (difference)

**Formula**:
```
Final Score = 0.5 × cos_sim + 0.3 × euclidean + 0.2 × manhattan
```

---

## Troubleshooting

### Issue: "Python not found"
**Solution**:
```bash
# Check if Python is installed
python --version

# If not, install from python.org
# Make sure to add to PATH during installation
```

### Issue: Camera not detected
**Solution**:
1. Check if webcam is connected
2. Grant permission in system settings
3. Try different camera ID in config
4. Test with: `python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`

### Issue: "Connection refused" on API calls
**Solution**:
1. Ensure backend is running (python app.py)
2. Check if port 5000 is not in use
3. Check firewall settings
4. Try: `netstat -ano | findstr :5000` (Windows)

### Issue: Poor matching accuracy
**Solutions**:
1. Ensure good lighting during enrollment
2. Keep eye centered and steady
3. Use same distance/angle for verification
4. Clean camera lens
5. Adjust CLAHE_CLIP_LIMIT in config

### Issue: Database locked
**Solution**:
1. Close all instances of application
2. Delete `database/iris_auth.db`
3. Restart system

### Issue: GUI not starting
**Solution**:
1. Verify all dependencies: `pip install -r requirements.txt`
2. Check if Tkinter is installed: `python -m tkinter`
3. On Linux: `sudo apt-get install python3-tk`

---

## Performance Specifications

| Operation | Time | Features |
|-----------|------|----------|
| Enrollment | 1.5-2s | 152 |
| Verification | 1.1-1.6s | 152 |
| Identification (5 users) | 1.5-2s | 152×5 |
| Feature Extraction | ~1.2s | 152 |

---

## Security Notes

✅ **Implemented**:
- Iris templates stored as binary data
- No plaintext password storage
- Database encryption ready (can implement SQLCipher)
- User authentication logs
- Access tracking

⚠️ **Recommendations**:
- Use HTTPS in production
- Implement SSL/TLS
- Add rate limiting
- Use environment variables for secrets
- Implement user roles and permissions
- Regular security audits

---

## File Structure

```
iris system with password/
├── backend/
│   └── app.py              # Flask REST API
├── gui/
│   └── gui.py              # Tkinter GUI application
├── database/
│   ├── iris_auth.db        # SQLite database
│   └── templates/          # Iris feature templates
├── config.py               # Configuration parameters
├── requirements.txt        # Python dependencies
├── start_windows.bat       # Windows startup script
├── start.sh                # Unix/Linux startup script
├── SETUP.md                # This file
├── README.md               # Project overview
└── assets/                 # Additional resources
```

---

## Support & Contact

For issues or questions:
1. Check Troubleshooting section
2. Review logs in terminal output
3. Check database status
4. Verify API connectivity

---

**Version**: 1.0  
**Last Updated**: January 2024  
**License**: MIT
