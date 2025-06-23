#!/usr/bin/env python3
"""
Setup and run script for PDF to Markdown/JSON/CSV Converter
Creates a virtual environment, installs dependencies, and runs the app
"""

import subprocess
import sys
import os
import platform
import venv
from pathlib import Path

def get_python_command():
    """Get the appropriate Python command based on the platform."""
    if platform.system() == "Windows":
        return "python"
    else:
        return "python3"

def get_pip_command():
    """Get the appropriate pip command based on the platform."""
    if platform.system() == "Windows":
        return "pip"
    else:
        return "pip3"

def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def create_virtual_environment():
    """Create a virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True
    
    print("📁 Creating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_venv_python_path():
    """Get the path to Python in the virtual environment."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def get_venv_pip_path():
    """Get the path to pip in the virtual environment."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")

def install_requirements():
    """Install requirements in the virtual environment."""
    python_path = get_venv_python_path()
    
    if not python_path.exists():
        print(f"❌ Python not found at {python_path}")
        return False
    
    # Upgrade pip first using python -m pip
    if not run_command(f'"{python_path}" -m pip install --upgrade pip', "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f'"{python_path}" -m pip install -r requirements.txt', "Installing requirements"):
        return False
    
    return True

def run_app():
    """Run the Streamlit app."""
    python_path = get_venv_python_path()
    
    if not python_path.exists():
        print(f"❌ Python not found at {python_path}")
        return False
    
    print("\n🎯 Choose which version to run:")
    print("1. Basic version (app.py)")
    print("2. Enhanced version with table extraction (app_simple.py)")
    print("3. Enhanced version with docling (app_enhanced.py) - may have compatibility issues")
    
    choice = input("\nEnter your choice (1, 2, or 3): ").strip()
    
    if choice == "3":
        app_file = "app_enhanced.py"
        print("🎯 Running enhanced version with docling support...")
    elif choice == "2":
        app_file = "app_simple.py"
        print("🎯 Running enhanced version with table extraction...")
    else:
        app_file = "app.py"
        print("🎯 Running basic version...")
    
    # Check if app file exists
    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found!")
        return False
    
    print(f"\n🌐 Starting Streamlit app: {app_file}")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the app")
    print("=" * 50)
    
    try:
        subprocess.run([str(python_path), "-m", "streamlit", "run", app_file])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")
        return False
    
    return True

def main():
    print("🚀 PDF to Markdown/JSON/CSV Converter Setup")
    print("=" * 50)
    
    # Check if Python is available
    python_cmd = get_python_command()
    if not run_command(f"{python_cmd} --version", "Checking Python installation", check=False):
        print("❌ Python is not installed or not in PATH")
        return
    
    # Create virtual environment
    if not create_virtual_environment():
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return
    
    print("✅ Setup completed successfully!")
    
    # Run the app
    run_app()

if __name__ == "__main__":
    main() 