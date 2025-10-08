#!/usr/bin/env python3
"""
Script to create an admin user.
"""

from app.db import create_user

def create_admin():
    username = 'admin'
    password = 'admin123'  # You can change this
    if create_user(username, password):
        print(f"Admin user '{username}' created successfully.")
    else:
        print(f"Failed to create admin user '{username}'. It may already exist.")

if __name__ == "__main__":
    create_admin()
