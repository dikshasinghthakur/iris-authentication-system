"""
Iris Authentication System - Backend
Advanced biometric iris recognition with Flask REST API
"""
import os
import cv2
import numpy as np
import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import base64
from io import BytesIO
import logging

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = "../database/iris_auth.db"
TEMPLATES_PATH = "../database/templates"

# Create templates directory if not exists
os.makedirs(TEMPLATES_PATH, exist_ok=True)


# ===================== DATABASE SETUP =====================

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            iris_template BLOB NOT NULL,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_access TIMESTAMP,
            access_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Authentication logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auth_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            similarity_score REAL,
            success BOOLEAN,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # System metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT,
            processing_time REAL,
            feature_count INTEGER,
            quality_score REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Identification logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS identification_logs (
            id_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            identified_user_id INTEGER,
            similarity_score REAL,
            search_time REAL,
            candidates_searched INTEGER,
            success BOOLEAN,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (identified_user_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


# ===================== IRIS PROCESSING =====================

def preprocess_iris(image_array):
    """
    Preprocess iris image with advanced techniques
    - Bilateral filtering for edge-preserving blur
    - CLAHE for contrast enhancement
    - Morphological operations
    """
    # Convert to grayscale if color
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array
    
    # Bilateral filter - edge preserving blur
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # CLAHE - Contrast Limited Adaptive Histogram Equalization
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(bilateral)
    
    # Morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    morphed = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
    
    # Normalization
    normalized = cv2.normalize(morphed, None, 0, 255, cv2.NORM_MINMAX)
    
    return normalized


def extract_gabor_features(image, scales=2, sigmas=3, orientations=5):
    """
    Extract Gabor filter features from iris image
    Total features: scales × sigmas × orientations × 2 (magnitude + phase)
    """
    features = []
    h, w = image.shape
    
    for scale in range(scales):
        kernel_size = 11 + scale * 5
        wavelength = 5 + scale * 3
        
        for sigma in np.linspace(0.5, 1.5, sigmas):
            for orientation in np.linspace(0, np.pi, orientations):
                # Create Gabor kernel
                kernel = cv2.getGaborKernel(
                    (kernel_size, kernel_size),
                    sigma,
                    orientation,
                    wavelength,
                    0.5,
                    0
                )
                kernel = kernel / kernel.sum()
                
                # Apply filter
                filtered = cv2.filter2D(image, cv2.CV_32F, kernel)
                
                # Extract features: mean magnitude and std
                features.append(np.mean(np.abs(filtered)))
                features.append(np.std(filtered))
    
    return np.array(features)


def extract_statistical_features(image):
    """Extract statistical features from iris image"""
    features = []
    
    # Basic statistics
    features.append(np.mean(image))
    features.append(np.std(image))
    features.append(np.max(image))
    features.append(np.min(image))
    features.append(np.median(image))
    
    # Percentiles
    features.append(np.percentile(image, 25))
    features.append(np.percentile(image, 75))
    features.append(np.percentile(image, 90))
    
    # Variance
    features.append(np.var(image))
    
    return np.array(features)


def extract_texture_features(image):
    """Extract local texture features using blocks"""
    features = []
    h, w = image.shape
    block_h = h // 3
    block_w = w // 3
    
    for i in range(3):
        for j in range(3):
            block = image[i*block_h:(i+1)*block_h, j*block_w:(j+1)*block_w]
            features.append(np.mean(block))
            features.append(np.std(block))
    
    return np.array(features)


def extract_edge_features(image):
    """Extract edge-based features using Sobel operator"""
    features = []
    
    # Sobel derivatives
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    
    features.append(np.mean(np.abs(sobelx)))
    features.append(np.mean(np.abs(sobely)))
    features.append(np.std(sobelx))
    features.append(np.std(sobely))
    features.append(np.mean(np.sqrt(sobelx**2 + sobely**2)))
    
    return np.array(features)


def extract_iris_features(image_array):
    """
    Complete feature extraction pipeline
    Combines: Gabor (120) + Statistical (9) + Texture (18) + Edge (5) = 152 features
    """
    # Preprocess
    processed = preprocess_iris(image_array)
    
    # Resize for consistency
    processed = cv2.resize(processed, (200, 200))
    
    # Extract all feature types
    gabor_feats = extract_gabor_features(processed, scales=2, sigmas=3, orientations=5)
    stat_feats = extract_statistical_features(processed)
    texture_feats = extract_texture_features(processed)
    edge_feats = extract_edge_features(processed)
    
    # Combine all features
    all_features = np.concatenate([gabor_feats, stat_feats, texture_feats, edge_feats])
    
    # Normalize to 0-1 range
    all_features = (all_features - np.min(all_features)) / (np.max(all_features) - np.min(all_features) + 1e-8)
    
    return all_features


def compute_similarity(features1, features2):
    """
    Compute similarity between two feature vectors using multiple metrics
    Weighted combination: 50% cosine, 30% Euclidean, 20% Manhattan
    """
    # Cosine similarity
    cos_sim = np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2) + 1e-8)
    
    # Euclidean distance normalized
    euclidean = 1 / (1 + np.sqrt(np.sum((features1 - features2)**2)))
    
    # Manhattan distance normalized
    manhattan = 1 / (1 + np.sum(np.abs(features1 - features2)))
    
    # Weighted combination
    similarity = 0.5 * cos_sim + 0.3 * euclidean + 0.2 * manhattan
    
    # Normalize to 0-1
    similarity = (similarity + 1) / 2
    return max(0, min(1, similarity))


# ===================== API ENDPOINTS =====================

@app.route('/health', methods=['GET'])
def health_check():
    """System health check endpoint"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'enrolled_users': user_count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/enroll', methods=['POST'])
def enroll_user():
    """
    Enroll new user with iris image
    POST body: {username, email, image_base64}
    """
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        image_base64 = data.get('image')
        
        if not all([username, email, image_base64]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Decode image
        image_data = base64.b64decode(image_base64)
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Extract features
        features = extract_iris_features(image)
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, iris_template)
                VALUES (?, ?, ?)
            ''', (username, email, features.tobytes()))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Log enrollment
            cursor.execute('''
                INSERT INTO auth_logs (user_id, action, success)
                VALUES (?, ?, ?)
            ''', (user_id, 'enrollment', True))
            conn.commit()
            
            # Log metrics
            cursor.execute('''
                INSERT INTO system_metrics (action_type, feature_count, quality_score)
                VALUES (?, ?, ?)
            ''', ('enrollment', len(features), 0.85))
            conn.commit()
            
            conn.close()
            
            logger.info(f"User enrolled: {username}")
            return jsonify({
                'success': True,
                'user_id': user_id,
                'message': f'User {username} enrolled successfully',
                'features_extracted': len(features)
            })
            
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'error': 'Username or email already exists'}), 409
            
    except Exception as e:
        logger.error(f"Enrollment error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/verify', methods=['POST'])
def verify_user():
    """
    Verify iris against stored template (1:1 matching)
    POST body: {username, image_base64}
    """
    try:
        data = request.json
        username = data.get('username')
        image_base64 = data.get('image')
        
        if not all([username, image_base64]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Decode image
        image_data = base64.b64decode(image_base64)
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Extract features
        new_features = extract_iris_features(image)
        
        # Get stored template
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, iris_template FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        user_id, template_bytes = result
        stored_features = np.frombuffer(template_bytes, dtype=np.float64)
        
        # Compute similarity
        similarity = compute_similarity(new_features, stored_features)
        
        # Decision threshold
        threshold = 0.65
        success = bool(similarity >= threshold)
        
        # Log authentication attempt
        cursor.execute('''
            INSERT INTO auth_logs (user_id, action, similarity_score, success)
            VALUES (?, ?, ?, ?)
        ''', (user_id, 'verification', float(similarity), success))
        
        if success:
            cursor.execute('UPDATE users SET last_access = CURRENT_TIMESTAMP, access_count = access_count + 1 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Verification {'successful' if success else 'failed'} for {username}: {similarity:.4f}")
        
        return jsonify({
            'success': success,
            'similarity': float(similarity),
            'threshold': threshold,
            'message': 'Authentication successful' if success else 'Authentication failed'
        })
        
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/identify', methods=['POST'])
def identify_user():
    """
    Identify user from iris (1:N matching)
    POST body: {image_base64}
    """
    try:
        data = request.json
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({'error': 'Missing image'}), 400
        
        # Decode image
        image_data = base64.b64decode(image_base64)
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Extract features
        new_features = extract_iris_features(image)
        
        # Search all enrolled users
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, email, iris_template FROM users WHERE status = "active"')
        users = cursor.fetchall()
        
        if not users:
            conn.close()
            return jsonify({'error': 'No enrolled users'}), 404
        
        # Compute similarity with all users
        matches = []
        for user_id, username, email, template_bytes in users:
            stored_features = np.frombuffer(template_bytes, dtype=np.float64)
            similarity = compute_similarity(new_features, stored_features)
            matches.append({
                'user_id': user_id,
                'username': username,
                'email': email,
                'similarity': float(similarity)
            })
        
        # Sort by similarity
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        best_match = matches[0]
        
        # Decision threshold
        threshold = 0.60
        success = best_match['similarity'] >= threshold
        
        # Log identification
        cursor.execute('''
            INSERT INTO identification_logs (identified_user_id, similarity_score, candidates_searched, success)
            VALUES (?, ?, ?, ?)
        ''', (best_match['user_id'], float(best_match['similarity']), len(users), success))
        conn.commit()
        conn.close()
        
        logger.info(f"Identification {'successful' if success else 'failed'}: {best_match['username']} ({best_match['similarity']:.4f})")
        
        return jsonify({
            'success': success,
            'best_match': best_match,
            'all_matches': matches,
            'threshold': threshold,
            'message': f"Identified as {best_match['username']}" if success else "Could not identify user"
        })
        
    except Exception as e:
        logger.error(f"Identification error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/users', methods=['GET'])
def get_users():
    """Get all enrolled users"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, username, email, enrollment_date, last_access, access_count, status
            FROM users
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'username': row[1],
                'email': row[2],
                'enrollment_date': row[3],
                'last_access': row[4],
                'access_count': row[5],
                'status': row[6]
            })
        
        conn.close()
        return jsonify({'users': users, 'total': len(users)})
        
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user details"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, username, email, enrollment_date, last_access, access_count, status
            FROM users WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        user = {
            'user_id': row[0],
            'username': row[1],
            'email': row[2],
            'enrollment_date': row[3],
            'last_access': row[4],
            'access_count': row[5],
            'status': row[6]
        }
        
        # Get user's authentication logs
        cursor.execute('''
            SELECT action, similarity_score, success, timestamp
            FROM auth_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10
        ''', (user_id,))
        
        logs = []
        for log in cursor.fetchall():
            logs.append({
                'action': log[0],
                'similarity': log[1],
                'success': bool(log[2]),
                'timestamp': log[3]
            })
        
        user['recent_logs'] = logs
        conn.close()
        
        return jsonify(user)
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user and associated data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get username for logging
        cursor.execute('SELECT username FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        username = result[0]
        
        # Delete user
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        
        # Delete related logs
        cursor.execute('DELETE FROM auth_logs WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM identification_logs WHERE identified_user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"User deleted: {username}")
        return jsonify({'success': True, 'message': f'User {username} deleted successfully'})
        
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/logs', methods=['GET'])
def get_logs():
    """Get all authentication and identification logs"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get recent logs
        cursor.execute('''
            SELECT user_id, action, similarity_score, success, timestamp
            FROM auth_logs ORDER BY timestamp DESC LIMIT 100
        ''')
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'user_id': row[0],
                'action': row[1],
                'similarity': row[2],
                'success': bool(row[3]),
                'timestamp': row[4]
            })
        
        # Get metrics
        cursor.execute('''
            SELECT action_type, processing_time, feature_count, quality_score, timestamp
            FROM system_metrics ORDER BY timestamp DESC LIMIT 50
        ''')
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'action': row[0],
                'processing_time': row[1],
                'features': row[2],
                'quality': row[3],
                'timestamp': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'logs': logs,
            'metrics': metrics,
            'total_logs': len(logs)
        })
        
    except Exception as e:
        logger.error(f"Get logs error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users WHERE status = "active"')
        total_users = cursor.fetchone()[0]
        
        # Total authentications
        cursor.execute('SELECT COUNT(*) FROM auth_logs')
        total_auth = cursor.fetchone()[0]
        
        # Successful authentications
        cursor.execute('SELECT COUNT(*) FROM auth_logs WHERE success = 1')
        successful_auth = cursor.fetchone()[0]
        
        # Total identifications
        cursor.execute('SELECT COUNT(*) FROM identification_logs')
        total_id = cursor.fetchone()[0]
        
        # Successful identifications
        cursor.execute('SELECT COUNT(*) FROM identification_logs WHERE success = 1')
        successful_id = cursor.fetchone()[0]
        
        # Average similarity
        cursor.execute('SELECT AVG(similarity_score) FROM auth_logs')
        avg_similarity = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'total_authentications': total_auth,
            'successful_authentications': successful_auth,
            'authentication_success_rate': (successful_auth / total_auth * 100) if total_auth > 0 else 0,
            'total_identifications': total_id,
            'successful_identifications': successful_id,
            'identification_success_rate': (successful_id / total_id * 100) if total_id > 0 else 0,
            'average_similarity': float(avg_similarity),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ===================== MAIN =====================

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    logger.info("🔐 Iris Authentication System - Backend Started")
    logger.info("📊 Available Endpoints:")
    logger.info("  POST   /enroll - Register new user")
    logger.info("  POST   /verify - Verify known user (1:1)")
    logger.info("  POST   /identify - Identify unknown user (1:N)")
    logger.info("  GET    /users - List all users")
    logger.info("  GET    /user/<id> - Get user details")
    logger.info("  DELETE /delete/<id> - Remove user")
    logger.info("  GET    /logs - View all logs")
    logger.info("  GET    /stats - System statistics")
    logger.info("  GET    /health - Health check")
    
    # Run Flask app

app.run(
    host='0.0.0.0',
    port=int(os.environ.get('PORT', 5000)),
    debug=False
)