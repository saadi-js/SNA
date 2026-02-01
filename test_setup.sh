#!/bin/bash
# Quick setup and test script for WSL/Linux

echo "=== Linux Server Health Analyzer - Setup Check ==="
echo ""

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "   ✓ Python3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "   ✓ Python found: $(python --version)"
else
    echo "   ✗ Python not found! Install with: sudo apt-get install python3"
    exit 1
fi

# Check pip
echo ""
echo "2. Checking pip..."
if command -v pip3 &> /dev/null; then
    echo "   ✓ pip3 found"
elif command -v pip &> /dev/null; then
    echo "   ✓ pip found"
else
    echo "   ✗ pip not found! Install with: sudo apt-get install python3-pip"
    exit 1
fi

# Check bash scripts
echo ""
echo "3. Checking bash scripts..."
if [ -d "bash" ]; then
    echo "   ✓ bash/ directory found"
    chmod +x bash/*.sh 2>/dev/null
    echo "   ✓ Made scripts executable"
    
    for script in bash/*.sh; do
        if [ -f "$script" ]; then
            echo "   ✓ Found: $(basename $script)"
        fi
    done
else
    echo "   ✗ bash/ directory not found!"
    exit 1
fi

# Check Python files
echo ""
echo "4. Checking Python files..."
if [ -f "analyzer.py" ]; then
    echo "   ✓ analyzer.py found"
else
    echo "   ✗ analyzer.py not found!"
    exit 1
fi

if [ -f "ai_engine.py" ]; then
    echo "   ✓ ai_engine.py found"
else
    echo "   ⚠ ai_engine.py not found (optional)"
fi

# Check dependencies
echo ""
echo "5. Checking Python dependencies..."
$PYTHON_CMD -c "import json, subprocess, sys, os, re, argparse, platform, shutil" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ Standard library imports OK"
else
    echo "   ✗ Standard library import failed!"
    exit 1
fi

# Check optional dependencies
echo ""
echo "6. Checking optional dependencies..."
$PYTHON_CMD -c "from dotenv import load_dotenv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ python-dotenv installed"
else
    echo "   ⚠ python-dotenv not installed (run: pip install python-dotenv)"
fi

$PYTHON_CMD -c "import google.generativeai" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ google-generativeai installed"
else
    echo "   ⚠ google-generativeai not installed (run: pip install google-generativeai)"
fi

# Test running analyzer
echo ""
echo "7. Testing analyzer (dry run)..."
$PYTHON_CMD analyzer.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Analyzer script is executable"
else
    echo "   ✗ Analyzer script has errors!"
    echo ""
    echo "   Running with verbose output:"
    $PYTHON_CMD analyzer.py --help
    exit 1
fi

echo ""
echo "=== Setup Check Complete ==="
echo ""
echo "To run the analyzer:"
echo "  $PYTHON_CMD analyzer.py"
echo ""
echo "Or with full report:"
echo "  $PYTHON_CMD analyzer.py --full-report"
echo ""
