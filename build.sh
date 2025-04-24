#!/usr/bin/env bash
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    tesseract-ocr-eng

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
