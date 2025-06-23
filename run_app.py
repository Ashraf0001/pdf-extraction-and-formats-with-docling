#!/usr/bin/env python3
"""
Startup script for PDF to Markdown/JSON/CSV Converter
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['streamlit', 'pandas', 'PyPDF2', 'pdfplumber']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies."""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please install manually:")
        print("pip install -r requirements.txt")
        return False

def main():
    print("🚀 Starting PDF to Markdown/JSON/CSV Converter")
    print("=" * 50)
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("\nInstalling dependencies...")
        if not install_dependencies():
            return
    else:
        print("✅ All dependencies are installed!")
    
    # Choose which app to run
    print("\nChoose which version to run:")
    print("1. Basic version (app.py)")
    print("2. Enhanced version with docling (app_enhanced.py)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "2":
        app_file = "app_enhanced.py"
        print("🎯 Running enhanced version with docling support...")
    else:
        app_file = "app.py"
        print("🎯 Running basic version...")
    
    # Check if app file exists
    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found!")
        return
    
    # Run the app
    print(f"\n🌐 Starting Streamlit app: {app_file}")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the app")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_file])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

if __name__ == "__main__":
    main() 