#!/bin/bash

echo "🚀 PDF to Markdown/JSON/CSV Converter - Virtual Environment Setup"
echo "================================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Run the setup script
python3 setup_and_run.py 