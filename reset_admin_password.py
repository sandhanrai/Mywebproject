#!/usr/bin/env python3
"""
Script to reset admin password.
"""

from app.db import get_db_connection, hash_password

def reset_admin_password():
    username = 'admin'
    new_password = 'admin'
    hashed = hash_password(new_password)
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET password_hash = %s WHERE username = %s", (hashed, username))
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Password for '{username}' reset to '{new_password}'.")
    else:
        print("Failed to connect to database.")

if __name__ == "__main__":
    reset_admin_password()
