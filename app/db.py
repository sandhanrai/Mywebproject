import mysql.connector
import bcrypt
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'health_symptom_checker')
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_users_table():
    """Create the users table if it doesn't exist."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username, password):
    """Create a new user in the database."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            connection.commit()
            return True
        except mysql.connector.IntegrityError:
            return False  # Username already exists
        finally:
            cursor.close()
            connection.close()
    return False

def authenticate_user(username, password):
    """Authenticate a user by checking username and password."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if result and verify_password(password, result[0]):
            return True
    return False

def get_user_id(username):
    """Get user ID from username."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] if result else None
    return None

def get_user_profile(user_id):
    """Get user profile information."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT age, gender, medical_history, allergies FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if result:
            return {
                'age': result[0],
                'gender': result[1],
                'medical_history': result[2],
                'allergies': result[3]
            }
    return None

def update_user_profile(user_id, age, gender, medical_history, allergies):
    """Update user profile information."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE users
            SET age = %s, gender = %s, medical_history = %s, allergies = %s
            WHERE id = %s
        """, (age, gender, medical_history, allergies, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False

def save_symptom_check(user_id, age, sex, symptoms, prediction):
    """Save a symptom check to the database."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        symptoms_json = json.dumps(symptoms)
        prediction_json = json.dumps(prediction)
        cursor.execute("""
            INSERT INTO symptom_checks (user_id, age, sex, symptoms, prediction)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, age, sex, symptoms_json, prediction_json))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False

def get_past_symptom_checks(user_id):
    """Get past symptom checks for a user."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, age, sex, symptoms, prediction, timestamp
            FROM symptom_checks
            WHERE user_id = %s
            ORDER BY timestamp DESC
        """, (user_id,))
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        checks = []
        for row in results:
            checks.append({
                'id': row[0],
                'age': row[1],
                'sex': row[2],
                'symptoms': json.loads(row[3]),
                'prediction': json.loads(row[4]),
                'timestamp': row[5]
            })
        return checks
    return []

# New functions for doctors

def get_doctors_by_pincode_and_specialty(pincode, specialty=None):
    """Retrieve doctors filtered by pincode and optionally by specialty."""
    connection = get_db_connection()
    doctors = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        if specialty:
            query = """
                SELECT id, name, specialty, address, pincode, phone
                FROM doctors
                WHERE pincode = %s AND specialty = %s
            """
            cursor.execute(query, (pincode, specialty))
        else:
            query = """
                SELECT id, name, specialty, address, pincode, phone
                FROM doctors
                WHERE pincode = %s
            """
            cursor.execute(query, (pincode,))
        doctors = cursor.fetchall()
        cursor.close()
        connection.close()
    return doctors

# New functions for admin dashboard analytics

def get_user_demographics():
    """Get user demographics: age, gender, location distribution."""
    connection = get_db_connection()
    demographics = {'age_groups': {}, 'genders': {}, 'locations': {}}
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT age, gender FROM users WHERE age IS NOT NULL AND gender IS NOT NULL
        """)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        for row in results:
            age = row['age']
            gender = row['gender']
            # Age groups
            if age < 18:
                group = 'Under 18'
            elif age < 35:
                group = '18-34'
            elif age < 50:
                group = '35-49'
            else:
                group = '50+'
            demographics['age_groups'][group] = demographics['age_groups'].get(group, 0) + 1
            # Genders
            demographics['genders'][gender] = demographics['genders'].get(gender, 0) + 1
        return demographics
    return demographics

def get_symptom_trends():
    """Get most common symptoms and trends."""
    connection = get_db_connection()
    symptoms = {}
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT symptoms FROM symptom_checks
        """)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        for row in results:
            symptom_data = json.loads(row['symptoms'])
            for symptom, present in symptom_data.items():
                if present:
                    symptoms[symptom] = symptoms.get(symptom, 0) + 1
        return dict(sorted(symptoms.items(), key=lambda x: x[1], reverse=True)[:10])
    return symptoms

def get_system_performance_metrics():
    """Get system performance metrics."""
    connection = get_db_connection()
    metrics = {'total_checks': 0, 'daily_checks': {}, 'weekly_checks': {}}
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as total, DATE(timestamp) as date FROM symptom_checks GROUP BY DATE(timestamp)
        """)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        for row in results:
            metrics['total_checks'] += row['total']
            date = str(row['date'])
            metrics['daily_checks'][date] = row['total']
        return metrics
    return metrics

def get_user_activity_logs():
    """Get user activity logs (recent logins, etc.)."""
    connection = get_db_connection()
    logs = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT username, created_at FROM users ORDER BY created_at DESC LIMIT 10
        """)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        logs = results
    return logs
