#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    tesseract-ocr-eng \  # English language pack
    tesseract-ocr-all   # All language packs (optional)

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
