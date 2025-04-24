#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Install Tesseract OCR and its dependencies
apt-get update
apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev

# Optional: Install additional language packs
# apt-get install -y tesseract-ocr-eng tesseract-ocr-fra tesseract-ocr-spa
