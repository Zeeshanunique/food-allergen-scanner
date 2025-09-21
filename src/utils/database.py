"""
Database Manager for Food Allergen Scanner
"""
import json
import os
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_profile import UserProfile
from models.product import Product

class DatabaseManager:
    """Manages data storage and retrieval for the application"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default database location
            db_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'data'
            )
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'food_scanner.db')
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create user profiles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER,
                        weight REAL,
                        allergies TEXT,
                        medications TEXT,
                        medical_conditions TEXT,
                        emergency_contact TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Create products table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        barcode TEXT UNIQUE,
                        name TEXT,
                        brand TEXT,
                        ingredients TEXT,
                        allergens TEXT,
                        nutritional_info TEXT,
                        category TEXT,
                        serving_size TEXT,
                        source TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Create scan history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scan_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        product_barcode TEXT,
                        scan_type TEXT,
                        risk_level TEXT,
                        allergens_detected TEXT,
                        recommendations TEXT,
                        scanned_at TEXT,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (id)
                    )
                ''')
                
                # Create consultation history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS consultations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        consultation_id TEXT UNIQUE,
                        user_id INTEGER,
                        consultation_type TEXT,
                        urgency TEXT,
                        symptoms TEXT,
                        doctor_assigned TEXT,
                        status TEXT,
                        requested_at TEXT,
                        resolved_at TEXT,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (id)
                    )
                ''')
                
                # Create allergen database table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS allergen_database (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        allergen_name TEXT,
                        category TEXT,
                        severity TEXT,
                        alternative_names TEXT,
                        description TEXT
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
    
    def save_user_profile(self, profile: UserProfile) -> bool:
        """Save or update user profile"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if profile exists
                cursor.execute('SELECT id FROM user_profiles WHERE name = ?', (profile.name,))
                existing = cursor.fetchone()
                
                profile_data = (
                    profile.name,
                    profile.age,
                    profile.weight,
                    json.dumps(profile.allergies),
                    json.dumps(profile.medications),
                    json.dumps(profile.medical_conditions),
                    profile.emergency_contact,
                    profile.created_at.isoformat() if profile.created_at else None,
                    profile.updated_at.isoformat() if profile.updated_at else None
                )
                
                if existing:
                    # Update existing profile
                    cursor.execute('''
                        UPDATE user_profiles 
                        SET age=?, weight=?, allergies=?, medications=?, 
                            medical_conditions=?, emergency_contact=?, updated_at=?
                        WHERE name=?
                    ''', profile_data[1:] + (profile.name,))
                else:
                    # Insert new profile
                    cursor.execute('''
                        INSERT INTO user_profiles 
                        (name, age, weight, allergies, medications, medical_conditions, 
                         emergency_contact, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', profile_data)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving user profile: {str(e)}")
            return False
    
    def load_user_profile(self, name: str) -> Optional[UserProfile]:
        """Load user profile by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM user_profiles WHERE name = ?
                ''', (name,))
                
                row = cursor.fetchone()
                if row:
                    profile_data = {
                        'name': row[1],
                        'age': row[2],
                        'weight': row[3],
                        'allergies': json.loads(row[4]) if row[4] else [],
                        'medications': json.loads(row[5]) if row[5] else [],
                        'medical_conditions': json.loads(row[6]) if row[6] else [],
                        'emergency_contact': row[7]
                    }
                    
                    profile = UserProfile.from_dict(profile_data)
                    if row[8]:  # created_at
                        profile.created_at = datetime.fromisoformat(row[8])
                    if row[9]:  # updated_at
                        profile.updated_at = datetime.fromisoformat(row[9])
                    
                    return profile
                
                return None
                
        except Exception as e:
            print(f"Error loading user profile: {str(e)}")
            return None
    
    def save_product(self, product: Product) -> bool:
        """Save or update product information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                product_data = (
                    product.barcode,
                    product.name,
                    product.brand,
                    json.dumps(product.ingredients),
                    json.dumps(product.allergens),
                    json.dumps(product.nutritional_info),
                    product.category,
                    product.serving_size,
                    'manual',  # source
                    product.created_at.isoformat() if product.created_at else None,
                    product.updated_at.isoformat() if product.updated_at else None
                )
                
                # Use INSERT OR REPLACE for upsert behavior
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (barcode, name, brand, ingredients, allergens, nutritional_info, 
                     category, serving_size, source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', product_data)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving product: {str(e)}")
            return False
    
    def load_product(self, barcode: str) -> Optional[Product]:
        """Load product by barcode"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM products WHERE barcode = ?
                ''', (barcode,))
                
                row = cursor.fetchone()
                if row:
                    product_data = {
                        'barcode': row[1],
                        'name': row[2],
                        'brand': row[3],
                        'ingredients': json.loads(row[4]) if row[4] else [],
                        'allergens': json.loads(row[5]) if row[5] else [],
                        'nutritional_info': json.loads(row[6]) if row[6] else {},
                        'category': row[7],
                        'serving_size': row[8]
                    }
                    
                    product = Product.from_dict(product_data)
                    if row[10]:  # created_at
                        product.created_at = datetime.fromisoformat(row[10])
                    if row[11]:  # updated_at
                        product.updated_at = datetime.fromisoformat(row[11])
                    
                    return product
                
                return None
                
        except Exception as e:
            print(f"Error loading product: {str(e)}")
            return None
    
    def save_scan_history(self, user_name: str, scan_data: Dict) -> bool:
        """Save scan history record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user ID
                cursor.execute('SELECT id FROM user_profiles WHERE name = ?', (user_name,))
                user_row = cursor.fetchone()
                user_id = user_row[0] if user_row else None
                
                scan_record = (
                    user_id,
                    scan_data.get('product_barcode', ''),
                    scan_data.get('scan_type', 'manual'),
                    scan_data.get('risk_level', 'unknown'),
                    json.dumps(scan_data.get('allergens_detected', [])),
                    json.dumps(scan_data.get('recommendations', [])),
                    datetime.now().isoformat()
                )
                
                cursor.execute('''
                    INSERT INTO scan_history 
                    (user_id, product_barcode, scan_type, risk_level, 
                     allergens_detected, recommendations, scanned_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', scan_record)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving scan history: {str(e)}")
            return False
    
    def get_scan_history(self, user_name: str, limit: int = 50) -> List[Dict]:
        """Get scan history for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT sh.*, p.name as product_name, p.brand 
                    FROM scan_history sh
                    JOIN user_profiles up ON sh.user_id = up.id
                    LEFT JOIN products p ON sh.product_barcode = p.barcode
                    WHERE up.name = ?
                    ORDER BY sh.scanned_at DESC
                    LIMIT ?
                ''', (user_name, limit))
                
                rows = cursor.fetchall()
                history = []
                
                for row in rows:
                    history.append({
                        'id': row[0],
                        'product_barcode': row[2],
                        'product_name': row[9] if row[9] else 'Unknown Product',
                        'brand': row[10] if row[10] else 'Unknown Brand',
                        'scan_type': row[3],
                        'risk_level': row[4],
                        'allergens_detected': json.loads(row[5]) if row[5] else [],
                        'recommendations': json.loads(row[6]) if row[6] else [],
                        'scanned_at': row[7]
                    })
                
                return history
                
        except Exception as e:
            print(f"Error getting scan history: {str(e)}")
            return []
    
    def save_consultation(self, consultation_data: Dict) -> bool:
        """Save consultation record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user ID if user profile provided
                user_id = None
                if consultation_data.get('user_profile'):
                    user_name = consultation_data['user_profile'].get('name', '')
                    if user_name:
                        cursor.execute('SELECT id FROM user_profiles WHERE name = ?', (user_name,))
                        user_row = cursor.fetchone()
                        user_id = user_row[0] if user_row else None
                
                consultation_record = (
                    consultation_data.get('id', ''),
                    user_id,
                    consultation_data.get('type', 'general'),
                    consultation_data.get('urgency', 'low'),
                    consultation_data.get('symptoms', ''),
                    json.dumps(consultation_data.get('assigned_doctor', {})),
                    consultation_data.get('status', 'pending'),
                    consultation_data.get('requested_at', datetime.now()).isoformat(),
                    consultation_data.get('resolved_at', '').isoformat() if consultation_data.get('resolved_at') else None
                )
                
                cursor.execute('''
                    INSERT OR REPLACE INTO consultations 
                    (consultation_id, user_id, consultation_type, urgency, symptoms, 
                     doctor_assigned, status, requested_at, resolved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', consultation_record)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving consultation: {str(e)}")
            return False
    
    def get_user_statistics(self, user_name: str) -> Dict:
        """Get user statistics and insights"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user ID
                cursor.execute('SELECT id FROM user_profiles WHERE name = ?', (user_name,))
                user_row = cursor.fetchone()
                if not user_row:
                    return {}
                
                user_id = user_row[0]
                
                # Get scan statistics
                cursor.execute('''
                    SELECT COUNT(*), risk_level 
                    FROM scan_history 
                    WHERE user_id = ? 
                    GROUP BY risk_level
                ''', (user_id,))
                
                scan_stats = {row[1]: row[0] for row in cursor.fetchall()}
                
                # Get consultation statistics
                cursor.execute('''
                    SELECT COUNT(*), consultation_type 
                    FROM consultations 
                    WHERE user_id = ? 
                    GROUP BY consultation_type
                ''', (user_id,))
                
                consultation_stats = {row[1]: row[0] for row in cursor.fetchall()}
                
                # Get most common allergens detected
                cursor.execute('''
                    SELECT allergens_detected 
                    FROM scan_history 
                    WHERE user_id = ? AND allergens_detected != "[]"
                    ORDER BY scanned_at DESC 
                    LIMIT 20
                ''', (user_id,))
                
                allergen_occurrences = {}
                for row in cursor.fetchall():
                    allergens = json.loads(row[0])
                    for allergen in allergens:
                        allergen_occurrences[allergen] = allergen_occurrences.get(allergen, 0) + 1
                
                return {
                    'total_scans': sum(scan_stats.values()),
                    'scan_risk_breakdown': scan_stats,
                    'total_consultations': sum(consultation_stats.values()),
                    'consultation_type_breakdown': consultation_stats,
                    'most_detected_allergens': sorted(
                        allergen_occurrences.items(), 
                        key=lambda x: x[1], 
                        reverse=True
                    )[:5],
                    'user_id': user_id
                }
                
        except Exception as e:
            print(f"Error getting user statistics: {str(e)}")
            return {}
    
    def cleanup_old_records(self, days: int = 365):
        """Clean up old records older than specified days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean old scan history
                cursor.execute('''
                    DELETE FROM scan_history 
                    WHERE scanned_at < ?
                ''', (cutoff_date,))
                
                # Clean old resolved consultations
                cursor.execute('''
                    DELETE FROM consultations 
                    WHERE resolved_at IS NOT NULL AND resolved_at < ?
                ''', (cutoff_date,))
                
                conn.commit()
                
                return True
                
        except Exception as e:
            print(f"Error cleaning up old records: {str(e)}")
            return False
    
    def export_user_data(self, user_name: str) -> Dict:
        """Export all user data"""
        try:
            # Get user profile
            profile = self.load_user_profile(user_name)
            if not profile:
                return {}
            
            # Get scan history
            scan_history = self.get_scan_history(user_name, limit=1000)
            
            # Get statistics
            statistics = self.get_user_statistics(user_name)
            
            return {
                'user_profile': profile.to_dict(),
                'scan_history': scan_history,
                'statistics': statistics,
                'export_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error exporting user data: {str(e)}")
            return {}