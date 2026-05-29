def check_import(name, import_str):
    try:
        exec(import_str)
        print(f"✓ {name} is installed correctly")
        return True
    except ImportError as e:
        print(f"✗ {name} FAILED: {e}")
        return False

print("=" * 50)
print("Checking all libraries...")
print("=" * 50)

checks = [
    ("Streamlit", "import streamlit"),
    ("PyMuPDF", "import fitz"),
    ("pdfplumber", "import pdfplumber"),
    ("spaCy", "import spacy"),
    ("scikit-learn", "import sklearn"),
    ("Pandas", "import pandas"),
    ("NumPy", "import numpy"),
    ("Plotly", "import plotly"),
    ("Sentence-Transformers", "from sentence_transformers import SentenceTransformer"),
    ("XGBoost", "import xgboost"),
    ("Pillow", "from PIL import Image"),
    ("FPDF", "from fpdf import FPDF"),
    ("WordCloud", "from wordcloud import WordCloud"),
    ("Joblib", "import joblib"),
    ("python-dotenv", "from dotenv import load_dotenv"),
    ("Matplotlib", "import matplotlib"),
    ("ReportLab", "from reportlab.pdfgen import canvas"),
]

all_passed = all(check_import(name, imp) for name, imp in checks)

print("=" * 50)

if all_passed:
    print("ALL LIBRARIES INSTALLED SUCCESSFULLY!")
else:
    print("Some libraries failed.")

print("=" * 50)

print("\nChecking spaCy English model...")

try:
    import spacy

    nlp = spacy.load("en_core_web_sm")

    doc = nlp("Python developer with 3 years experience")

    print("✓ spaCy English model loaded successfully")
    print([token.text for token in doc])

except Exception as e:
    print(f"✗ spaCy model failed: {e}")
