#!/usr/bin/env python3
"""
Setup script for AI Shopping Assistant MVP
Automates installation and configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    return True

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("config.env.example")
    
    if not env_example.exists():
        print("❌ config.env.example not found")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists. Skipping...")
        return True
    
    # Copy example to .env
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from template")
    
    # Check if OpenAI API key is set
    with open(env_file, 'r') as f:
        content = f.read()
        if "your_openai_api_key_here" in content:
            print("⚠️  Please update your OpenAI API key in the .env file")
            print("   Edit .env and replace 'your_openai_api_key_here' with your actual API key")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["logs", "data"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        "langchain",
        "langchain_openai", 
        "openai",
        "fastapi",
        "uvicorn",
        "pydantic",
        "requests"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    return True

def create_startup_scripts():
    """Create startup scripts for easy launching"""
    print("🚀 Creating startup scripts...")
    
    # Windows batch file
    windows_script = """@echo off
echo Starting AI Shopping Assistant MVP...
echo.
echo Starting Mock E-commerce APIs...
start "Mock APIs" python mock_apis.py
timeout /t 3 /nobreak >nul
echo.
echo Starting Shopping Assistant Web Interface...
start "Shopping Assistant" python web_interface.py
timeout /t 3 /nobreak >nul
echo.
echo Opening web interface...
start http://localhost:8000
echo.
echo Shopping Assistant is starting up!
echo Mock APIs: http://localhost:8001
echo Web Interface: http://localhost:8000
echo.
pause
"""
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting AI Shopping Assistant MVP..."
echo ""
echo "Starting Mock E-commerce APIs..."
python mock_apis.py &
MOCK_PID=$!
sleep 3
echo ""
echo "Starting Shopping Assistant Web Interface..."
python web_interface.py &
WEB_PID=$!
sleep 3
echo ""
echo "Opening web interface..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000
elif command -v open &> /dev/null; then
    open http://localhost:8016
fi
echo ""
echo "Shopping Assistant is starting up!"
echo "Mock APIs: http://localhost:8015"
echo "Web Interface: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"
trap "kill $MOCK_PID $WEB_PID; exit" INT
wait
"""
    
    # Write scripts
    with open("start_windows.bat", "w") as f:
        f.write(windows_script)
    
    with open("start_unix.sh", "w") as f:
        f.write(unix_script)
    
    # Make Unix script executable
    if os.name != 'nt':  # Not Windows
        os.chmod("start_unix.sh", 0o755)
    
    print("✅ Created startup scripts:")
    print("   - start_windows.bat (Windows)")
    print("   - start_unix.sh (Unix/Linux/Mac)")
    
    return True

def main():
    """Main setup function"""
    print("🛍️ AI Shopping Assistant MVP Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed at environment setup")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Setup failed at directory creation")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed at import testing")
        sys.exit(1)
    
    # Create startup scripts
    if not create_startup_scripts():
        print("❌ Setup failed at startup script creation")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("=" * 40)
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run the startup script:")
    if os.name == 'nt':  # Windows
        print("   start_windows.bat")
    else:
        print("   ./start_unix.sh")
    print("3. Open http://localhost:8000 in your browser")
    print("4. Start chatting with your shopping assistant!")
    print("\n📚 For more information, see README.md")
    print("\n🚀 Happy shopping! 🛍️")

if __name__ == "__main__":
    main() 