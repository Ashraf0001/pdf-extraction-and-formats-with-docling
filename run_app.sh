#!/bin/bash

echo "🚀 Starting PDF to Markdown/JSON/CSV Converter"
echo "================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Run the startup script
python3 run_app.py 