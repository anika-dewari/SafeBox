#!/bin/bash
# SafeBox Real System Launcher
# This script runs the SafeBox CLI with proper terminal handling

cd "$(dirname "$0")"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  SafeBox requires root privileges"
    echo "🔄 Relaunching with sudo..."
    exec sudo "$0" "$@"
fi

# Run the CLI
python3 cli/real_safebox_cli.py
