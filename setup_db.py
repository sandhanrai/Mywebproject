#!/usr/bin/env python3
"""
Database setup script for Health Symptom Checker.
This script creates the MySQL database and tables if they don't exist.
"""

import mysql.connector
import os
from dotenv import load_dotenv
from app.db import get_db_connection

load_dotenv()

def create_database():
    """Create the database if it doesn't exist."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS health_symptom_checker")
        print("Database 'health_symptom_checker' created or already exists.")
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

def setup_tables():
    """Set up the necessary tables."""
    from app.db import create_users_table
    create_users_table()
    print("Users table created or already exists.")

    # Alter users table to add profile columns
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Check and add columns one by one
            cursor.execute("SHOW COLUMNS FROM users LIKE 'age'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN age INT")
            cursor.execute("SHOW COLUMNS FROM users LIKE 'gender'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN gender VARCHAR(10)")
            cursor.execute("SHOW COLUMNS FROM users LIKE 'medical_history'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN medical_history TEXT")
            cursor.execute("SHOW COLUMNS FROM users LIKE 'allergies'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN allergies TEXT")
            cursor.execute("SHOW COLUMNS FROM users LIKE 'chronic_conditions'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN chronic_conditions TEXT")
            cursor.execute("SHOW COLUMNS FROM users LIKE 'medications'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN medications TEXT")
            cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
            cursor.execute("SHOW COLUMNS FROM users LIKE 'notifications'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN notifications VARCHAR(10) DEFAULT 'enabled'")
            connection.commit()
            print("Users table altered with profile columns.")
        except mysql.connector.Error as err:
            print(f"Error altering users table: {err}")
        finally:
            cursor.close()
            connection.close()

    # Create symptom_checks table
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS symptom_checks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    age INT,
                    sex VARCHAR(10),
                    symptoms JSON,
                    prediction JSON,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            connection.commit()
            print("Symptom_checks table created or already exists.")
        except mysql.connector.Error as err:
            print(f"Error creating symptom_checks table: {err}")
        finally:
            cursor.close()
            connection.close()

    # Create doctors table
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    specialty VARCHAR(255),
                    address TEXT,
                    pincode VARCHAR(20),
                    phone VARCHAR(20)
                )
            """)
            connection.commit()
            print("Doctors table created or already exists.")
        except mysql.connector.Error as err:
            print(f"Error creating doctors table: {err}")
        finally:
            cursor.close()
            connection.close()

    # Insert sample doctors data if table is empty
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM doctors")
        count = cursor.fetchone()[0]
        if count == 0:
            try:
                sample_doctors = [
                    ("Dr. John Smith", "general", "123 Main St, City", "12345", "555-1234"),
                    ("Dr. Alice Johnson", "cardiology", "456 Heart Rd, City", "12345", "555-5678"),
                    ("Dr. Bob Lee", "dermatology", "789 Skin Ave, City", "67890", "555-9012"),
                    ("Dr. Carol White", "neurology", "321 Brain Blvd, City", "67890", "555-3456"),
                    ("Dr. David Green", "pediatrics", "654 Child St, City", "12345", "555-7890")
                ]
                cursor.executemany("""
                    INSERT INTO doctors (name, specialty, address, pincode, phone)
                    VALUES (%s, %s, %s, %s, %s)
                """, sample_doctors)
                connection.commit()
                print("Sample doctors data inserted.")
            except mysql.connector.Error as err:
                print(f"Error inserting sample doctors data: {err}")
            finally:
                cursor.close()
                connection.close()
        else:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("Setting up database...")
    create_database()
    setup_tables()
    print("Database setup complete.")
