#!/bin/bash

# Build script for tither.py
# Creates a standalone Linux binary using PyInstaller

set -e

echo "Building tither.py for Linux..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install --break-system-packages pyinstaller
fi

# Check if the Python file exists
if [ ! -f "tither.py" ]; then
    echo "Error: tither.py not found in current directory"
    exit 1
fi

# Build the executable
echo "Creating standalone executable..."
pyinstaller --onefile --name tither \
    --windowed \
    --clean \
    tither.py

echo "Build complete!"
echo "Executable created: dist/tither"
echo ""
echo "To run: ./dist/tither"
