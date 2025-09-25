#!/usr/bin/env python3
"""
Setup script for Health Symptom Checker Web App
This script installs dependencies and creates necessary directories
"""

import os
import subprocess
import sys

def create_directories():
    """Create necessary directories for the project"""
    directories = [
        'models',
        'data',
        'src',
        'app'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}/")

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    
    try:
        # Check if pip is available
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
        
        # Install packages from requirements.txt
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Dependencies installed successfully!")
        else:
            print("✗ Error installing dependencies:")
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError:
        print("✗ pip is not available. Please install pip first.")
        return False
    except FileNotFoundError:
        print("✗ Python executable not found. Please ensure Python is installed.")
        return False
    
    return True

def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version >= required_version:
        print(f"✓ Python version {sys.version.split()[0]} is compatible")
        return True
    else:
        print(f"✗ Python {required_version[0]}.{required_version[1]}+ required")
        print(f"  Current version: {sys.version.split()[0]}")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("Health Symptom Checker - Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\nCreating project structure...")
    create_directories()
    
    # Install dependencies
    print("\nInstalling packages...")
    if not install_dependencies():
        print("\nPlease install dependencies manually:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Setup completed successfully! 🎉")
    print("\nNext steps:")
    print("1. Train the model: python src/model_training.py")
    print("2. Run the app: streamlit run app/app.py")
    print("3. Open http://localhost:8501 in your browser")
    print("=" * 50)

if __name__ == "__main__":
    main()
