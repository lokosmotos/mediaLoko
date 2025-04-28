#!/bin/bash
pip install --upgrade pip
pip install numpy==1.23.5 --force-reinstall
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download zh_core_web_sm
