#!/bin/bash

# SafeBox WSL Environment Setup Script
# Run this script in WSL after completing Ubuntu user setup

set -e  # Exit on error

echo "🔧 SafeBox WSL Environment Setup"
echo "================================"
echo ""

# Update package lists
echo "📦 Updating package lists..."
sudo apt update

# Install build essentials
echo "🛠️  Installing build tools..."
sudo apt install -y build-essential cmake gcc g++ pkg-config libseccomp-dev

# Install Python and pip
echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install required Python packages
echo "📚 Installing Python dependencies..."
pip3 install --break-system-packages flask==3.1.2 flask-cors==6.0.1 fastapi==0.119.0 uvicorn==0.37.0 psutil==7.1.0 rich==14.2.0 pytest==8.4.2

# Check for cgroups v2
echo "🔍 Checking cgroups v2 support..."
if [ -d "/sys/fs/cgroup/cgroup.controllers" ]; then
    echo "✅ cgroups v2 is available"
else
    echo "⚠️  cgroups v2 not detected - some features may be limited"
fi

# Navigate to project directory (Windows path mounted in WSL)
PROJECT_DIR="/mnt/c/Users/Dell/Documents/GitHub/SafeBox_"

if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    echo "📁 Changed to project directory: $PROJECT_DIR"
    
    # Build everything
    echo "🏗️  Building SafeBox components..."
    make real-system
    
    echo "✅ Build completed successfully!"
    
else
    echo "⚠️  Project directory not found at $PROJECT_DIR"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              ✅ Setup Complete!                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "   1. Run Real System (requires sudo):"
echo "      cd /mnt/c/Users/Dell/Documents/GitHub/SafeBox_"
echo "      sudo python3 cli/real_safebox_cli.py"
echo ""
echo "   2. Or run simulation mode (no sudo):"
echo "      cd web && python3 app.py"
echo "      cd cli && python3 safebox_cli.py load-example"
echo ""
echo "   3. Build individual components:"
echo "      make build-c      # C components"
echo "      make build-cpp    # C++ cgroup agent"
echo ""
echo "📖 System Flow:"
echo "   User → Banker's Algorithm → cgroups → SafeBox → App"
echo ""
echo "💡 Tip: Open VS Code with 'code .' for WSL integration"

