#!/bin/bash
# setup.sh — runs on Streamlit Cloud before the app starts
# Downloads the spaCy English model required by our NLP engine

pip install -r requirements.txt
python -m spacy download en_core_web_lg
python src/data_pipeline.py