#!/bin/bash

# PDF OCR Tool - One-Line Installer Script
# This script demonstrates how users can run the tool with one command

set -e

echo "=================================================="
echo "PDF OCR Tool - Quick Setup"
echo "=================================================="
echo ""

# Check if on macOS or Linux
OS=$(uname -s)

echo "Step 1: Installing system dependencies..."
echo ""

if [ "$OS" = "Darwin" ]; then
    # macOS
    echo "Detected macOS"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install dependencies
    echo "Installing Tesseract and Poppler..."
    brew install tesseract poppler
    
elif [ "$OS" = "Linux" ]; then
    # Linux
    echo "Detected Linux"
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        echo "Installing via apt-get..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr poppler-utils
    elif command -v dnf &> /dev/null; then
        echo "Installing via dnf..."
        sudo dnf install -y tesseract poppler-utils
    elif command -v yum &> /dev/null; then
        echo "Installing via yum..."
        sudo yum install -y tesseract poppler-utils
    else
        echo "Error: Unable to detect package manager"
        exit 1
    fi
else
    echo "Unsupported operating system: $OS"
    exit 1
fi

echo ""
echo "✓ System dependencies installed!"
echo ""

echo "Step 2: Installing uv (if not already installed)..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the shell profile to get uv in PATH
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
fi

echo "✓ uv is installed!"
echo ""

echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "You can now run the PDF OCR tool with:"
echo ""
echo "  cd $(pwd)"
echo "  uvx --from . pdf-ocr"
echo ""
echo "Or with a PDF file directly:"
echo ""
echo "  uvx --from . pdf-ocr document.pdf --pages 4-5"
echo ""
echo "For help:"
echo ""
echo "  uvx --from . pdf-ocr --help"
echo ""
echo "=================================================="
