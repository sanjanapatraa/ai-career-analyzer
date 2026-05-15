# src/career_recommender.py
# ══════════════════════════════════════════════════════════════════════════
# CAREER RECOMMENDATION ENGINE
#
# What this file does:
#   1. Loads the processed training data from Phase 3
#   2. Trains TWO classifiers (Random Forest + XGBoost)
#   3. Combines them into an Ensemble (voting classifier)
#   4. Evaluates accuracy with full classification report
#   5. Saves trained models to disk
#   6. Provides a predict() function for the Streamlit app
#
# WHY TWO MODELS?
#   Random Forest = many decision trees voting together
#   XGBoost = gradient boosting (learns from previous mistakes)
#   Ensemble = combine both → usually beats either alone
#   Think of it like asking two expert opinions and averaging them.
# ══════════════════════════════════════════════════════════════════════════

import os
import json
import logging
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import joblib                    # Save/load Python objects to .pkl files

# Scikit-learn models
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
import scipy.sparse as sp        # Sparse matrices (memory-efficient for TF-IDF)

# XGBoost — gradient boosting
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not installed. Using Random Forest only.")

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
MODELS_DIR    = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — DATA LOADER
# ════════════════════════════════════════════════════════════════════════════

def load_training_data():
    """
    Load the preprocessed training data saved in Phase 3.

    Returns:
        X_train, X_test, y_train, y_test, label_encoder, feature_info

    What are X and y?
        X = features (the inputs to the model)
            In our case: TF-IDF word scores + engineered features
            Shape: (num_resumes, num_features) e.g. (480, 5030)

        y = labels (what we're predicting)
            In our case: career category as a number (0, 1, 2, ...)
            Shape: (num_resumes,) e.g. (480,)

    Train vs Test split:
        Training data: used to TEACH the model (80%)
        Test data: used to EVALUATE the model on unseen data (20%)
        We NEVER train on test data — that would be cheating!
    """
    logger.info("Loading training data from Phase 3...")

    required = ['X_train.pkl', 'X_test.pkl', 'y_train.pkl',
                'y_test.pkl', 'feature_info.json']

    # Check if Phase 3 was completed
    for fname in required:
        path = os.path.join(PROCESSED_DIR, fname)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing: {path}\n"
                "Please run Phase 3 first: python src/data_pipeline.py"
            )

    # Load the four data splits saved in Phase 3
    X_train = joblib.load(os.path.join(PROCESSED_DIR, 'X_train.pkl'))
    X_test  = joblib.load(os.path.join(PROCESSED_DIR, 'X_test.pkl'))
    y_train = joblib.load(os.path.join(PROCESSED_DIR, 'y_train.pkl'))
    y_test  = joblib.load(os.path.join(PROCESSED_DIR, 'y_test.pkl'))

    # Load the label encoder (maps numbers back to career names)
    encoder_path = os.path.join(MODELS_DIR, 'label_encoder.pkl')
    label_encoder = joblib.load(encoder_path)

    # Load feature metadata
    with open(os.path.join(PROCESSED_DIR, 'feature_info.json')) as f:
        feature_info = json.load(f)

    logger.info(f"Training set: {X_train.shape[0]} samples, {X_train.shape[1]} features")
    logger.info(f"Test set:     {X_test.shape[0]} samples")
    logger.info(f"Categories:   {len(label_encoder.classes_)}")

    return X_train, X_test, y_train, y_test, label_encoder, feature_info


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — MODEL DEFINITIONS
# ════════════════════════════════════════════════════════════════════════════

def build_random_forest(n_estimators=200):
    """
    Build a Random Forest classifier.

    WHAT IS RANDOM FOREST? (Toddler explanation)
    Imagine you want to guess if a resume belongs to a "Data Scientist".
    Instead of asking ONE expert, you ask 200 experts (trees).
    Each expert looks at a RANDOM subset of features.
    The majority vote wins.
    This prevents any single expert from being overconfident (overfitting).

    Hyperparameters explained:
        n_estimators=200:   Number of trees in the forest
                            More trees = more stable, but slower training
        max_depth=30:       How deep each tree can grow
                            Deeper = learns more patterns, but may overfit
        min_samples_split=3: A node splits only if it has 3+ samples
                             Prevents trees from memorizing tiny details
        class_weight='balanced': Give equal importance to all career categories
                                 even if some have fewer resumes
        random_state=42:    Makes results reproducible (same result every run)
    """
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=30,
        min_samples_split=3,
        min_samples_leaf=1,
        max_features='sqrt',      # Each tree uses sqrt(total features) randomly
        class_weight='balanced',
        n_jobs=-1,                # Use ALL CPU cores for speed
        random_state=42,
        verbose=0,
    )


def build_xgboost():
    """
    Build an XGBoost classifier.

    WHAT IS XGBOOST? (Simple explanation)
    XGBoost learns by making many WEAK learners that correct each other.

    Imagine playing darts:
    - First dart: terrible throw (weak learner)
    - Second dart: aims to fix the first throw's error
    - Third dart: fixes the second throw's error
    - ... repeat 200 times
    - Final result: very accurate throw (strong learner)

    This is called "gradient boosting" — each model boosts the previous one.

    Hyperparameters:
        n_estimators=200:   Number of boosting rounds
        max_depth=6:        Max tree depth (XGBoost uses shallower trees)
        learning_rate=0.1:  How much each tree corrects the previous
                            Lower = more careful learning, needs more trees
        use_label_encoder=False: Suppress deprecation warning
        eval_metric='mlogloss': Multi-class log loss (standard for classification)
    """
    if not XGBOOST_AVAILABLE:
        return None

    return xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,           # Each tree uses 80% of training samples
        colsample_bytree=0.8,    # Each tree uses 80% of features
        use_label_encoder=False,
        eval_metric='mlogloss',
        n_jobs=-1,
        random_state=42,
        verbosity=0,
    )


def build_logistic_regression():
    """
    Logistic Regression — fast baseline model.

    Despite the name, it's a CLASSIFICATION model (not regression).
    It learns a straight-line boundary between career classes.
    Useful as a fast, interpretable baseline.

    C=5.0: Regularization strength (higher = less regularization)
    max_iter=1000: Training iterations
    """
    return LogisticRegression(
        C=5.0,
        max_iter=1000,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        solver='saga',           # Fast solver for large datasets
    )


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — TRAINING PIPELINE
# ════════════════════════════════════════════════════════════════════════════

def train_all_models(X_train, X_test, y_train, y_test, label_encoder):
    """
    Train all classifiers and evaluate them.

    Args:
        X_train: Training feature matrix
        X_test:  Test feature matrix
        y_train: Training labels (numbers)
        y_test:  Test labels (numbers)
        label_encoder: Maps numbers → career names

    Returns:
        Dictionary: {model_name: trained_model}
        Dictionary: {model_name: accuracy_score}
    """
    logger.info("=" * 60)
    logger.info("PHASE 5: TRAINING ML MODELS")
    logger.info("=" * 60)

    trained_models = {}
    results = {}

    # Fix NaN values
    import numpy as np

    if hasattr(X_train, "toarray"):
        X_train = np.nan_to_num(X_train.toarray())
        X_test = np.nan_to_num(X_test.toarray())
    else:
        X_train = np.nan_to_num(X_train)
        X_test = np.nan_to_num(X_test)

    # ── Model 1: Random Forest ─────────────────────────────────────────────
    logger.info("\nTraining Random Forest (200 trees)...")
    rf = build_random_forest()
    rf.fit(X_train, y_train)      # TRAINING HAPPENS HERE

    rf_pred  = rf.predict(X_test) # Make predictions on unseen test data
    rf_acc   = accuracy_score(y_test, rf_pred)

    trained_models['random_forest'] = rf
    results['random_forest'] = rf_acc
    logger.info(f"Random Forest Accuracy: {rf_acc:.4f} ({rf_acc*100:.1f}%)")

    # ── Model 2: XGBoost ───────────────────────────────────────────────────
    if XGBOOST_AVAILABLE:
        logger.info("\nTraining XGBoost (200 boosting rounds)...")
        xgb_model = build_xgboost()
        xgb_model.fit(X_train, y_train)

        xgb_pred = xgb_model.predict(X_test)
        xgb_acc  = accuracy_score(y_test, xgb_pred)

        trained_models['xgboost'] = xgb_model
        results['xgboost'] = xgb_acc
        logger.info(f"XGBoost Accuracy: {xgb_acc:.4f} ({xgb_acc*100:.1f}%)")

    # ── Model 3: Logistic Regression ──────────────────────────────────────
    logger.info("\nTraining Logistic Regression...")
    lr = build_logistic_regression()
    lr.fit(X_train, y_train)

    lr_pred = lr.predict(X_test)
    lr_acc  = accuracy_score(y_test, lr_pred)

    trained_models['logistic_regression'] = lr
    results['logistic_regression'] = lr_acc
    logger.info(f"Logistic Regression Accuracy: {lr_acc:.4f} ({lr_acc*100:.1f}%)")

    # ── Model 4: Ensemble (Voting Classifier) ──────────────────────────────
    # Combine all trained models into one ensemble
    # 'soft' voting: average the probability scores from all models
    # This is usually MORE accurate than any single model
    logger.info("\nBuilding Ensemble (Voting Classifier)...")

    estimators = [('rf', rf), ('lr', lr)]
    if XGBOOST_AVAILABLE:
        estimators.append(('xgb', trained_models['xgboost']))

    # VotingClassifier with voting='soft' averages probabilities
    # Each model votes: "I think this is Data Scientist with 85% confidence"
    # The ensemble averages all votes → picks the winner
    ensemble = VotingClassifier(
        estimators=estimators,
        voting='soft',   # Use probability scores, not just yes/no votes
        n_jobs=-1,
    )

    # NOTE: VotingClassifier needs to re-fit its internal models
    # Even though they're already trained above
    ensemble.fit(X_train, y_train)

    ens_pred = ensemble.predict(X_test)
    ens_acc  = accuracy_score(y_test, ens_pred)

    trained_models['ensemble'] = ensemble
    results['ensemble'] = ens_acc
    logger.info(f"Ensemble Accuracy: {ens_acc:.4f} ({ens_acc*100:.1f}%)")

    # ── Print full evaluation report ───────────────────────────────────────
    best_model_name = max(results, key=results.get)
    best_model      = trained_models[best_model_name]
    best_pred       = best_model.predict(X_test)

    logger.info("\n" + "=" * 60)
    logger.info("MODEL COMPARISON")
    logger.info("=" * 60)
    for name, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
        bar = '█' * int(acc * 40)
        logger.info(f"  {name:<25} {acc*100:>6.1f}%  {bar}")

    logger.info(f"\nBest Model: {best_model_name} ({results[best_model_name]*100:.1f}%)")

    logger.info("\n" + "=" * 60)
    logger.info("DETAILED CLASSIFICATION REPORT (Ensemble)")
    logger.info("=" * 60)
    # classification_report shows precision, recall, f1-score per class
    # precision = of all predicted "Data Scientist", how many were correct?
    # recall    = of all actual "Data Scientists", how many did we find?
    # f1-score  = harmonic mean of precision and recall (balance of both)
    report = classification_report(
        y_test,
        ens_pred,
        target_names=label_encoder.classes_,
        zero_division=0,
    )
    logger.info("\n" + report)

    # ── Cross-validation ───────────────────────────────────────────────────
    # Cross-validation: split data 5 ways, train on 4 folds, test on 1
    # Repeat for each fold → get 5 accuracy scores → take average
    # This gives a more reliable estimate than a single train/test split
    logger.info("Running 5-fold Cross-Validation on best model...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # We run CV on the Random Forest (faster than ensemble)
    cv_scores = cross_val_score(rf, X_train, y_train, cv=cv, scoring='accuracy', n_jobs=-1)
    logger.info(f"CV Scores: {[f'{s:.3f}' for s in cv_scores]}")
    logger.info(f"CV Mean: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    return trained_models, results


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SAVE MODELS
# ════════════════════════════════════════════════════════════════════════════

def save_models(trained_models: dict, results: dict):
    """
    Save all trained models to disk as .pkl files.

    joblib.dump() serializes the entire model object to a binary file.
    joblib.load() restores it exactly, ready to make predictions.
    We use joblib instead of pickle because it's faster for large numpy arrays.
    """
    logger.info("\n" + "=" * 60)
    logger.info("SAVING MODELS")
    logger.info("=" * 60)

    save_map = {
        'random_forest':        'career_classifier_rf.pkl',
        'xgboost':              'career_classifier_xgb.pkl',
        'logistic_regression':  'career_classifier_lr.pkl',
        'ensemble':             'career_classifier_ensemble.pkl',
    }

    for model_name, filename in save_map.items():
        if model_name in trained_models:
            path = os.path.join(MODELS_DIR, filename)
            joblib.dump(trained_models[model_name], path, compress=3)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            logger.info(f"Saved {model_name}: {filename} ({size_mb:.1f} MB)")

    # Save results summary as JSON
    results_path = os.path.join(MODELS_DIR, 'model_results.json')
    with open(results_path, 'w') as f:
        json.dump({
            'accuracy_scores': results,
            'best_model': max(results, key=results.get),
        }, f, indent=2)

    logger.info(f"Saved results summary: model_results.json")


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5 — PREDICTION ENGINE (used by Streamlit app)
# ════════════════════════════════════════════════════════════════════════════

class CareerRecommender:
    """
    Production-ready career recommender used by the Streamlit app.

    Loads saved models and provides:
    - predict()        → top career recommendation
    - predict_top_n()  → top N career recommendations with scores
    - get_skill_gaps() → what skills to learn for a target career
    """

    def __init__(self):
        """Load all saved models and encoders on startup."""
        logger.info("Loading CareerRecommender...")
        self.models = {}
        self.label_encoder = None
        self.vectorizer    = None
        self.feature_info  = None
        self._load_all()

    def _load_all(self):
        """Load every saved artifact from disk."""
        try:
            # Load label encoder
            enc_path = os.path.join(MODELS_DIR, 'label_encoder.pkl')
            if os.path.exists(enc_path):
                self.label_encoder = joblib.load(enc_path)
                logger.info(f"Label encoder loaded: {len(self.label_encoder.classes_)} classes")

            # Load TF-IDF vectorizer (trained in Phase 3)
            vec_path = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
            if os.path.exists(vec_path):
                self.vectorizer = joblib.load(vec_path)
                logger.info("TF-IDF vectorizer loaded")

            # Load models
            model_files = {
                'ensemble':    'career_classifier_ensemble.pkl',
                'random_forest': 'career_classifier_rf.pkl',
                'xgboost':     'career_classifier_xgb.pkl',
            }

            for name, fname in model_files.items():
                path = os.path.join(MODELS_DIR, fname)
                if os.path.exists(path):
                    self.models[name] = joblib.load(path)
                    logger.info(f"Loaded model: {name}")

            # Load feature info
            fi_path = os.path.join(PROCESSED_DIR, 'feature_info.json')
            if os.path.exists(fi_path):
                with open(fi_path) as f:
                    self.feature_info = json.load(f)

            if not self.models:
                logger.warning("No trained models found. Run train_models() first.")

        except Exception as e:
            logger.error(f"Error loading models: {e}")

    def _prepare_features(self, resume_text: str,
                          resume_data: dict = None) -> sp.csr_matrix:
        """
        Convert a resume text into the feature vector the model expects.

        This MUST match exactly what we did in Phase 3 data_pipeline.py.
        The model was trained on a specific feature format.
        If we give it different features, predictions will be wrong.

        Args:
            resume_text: Cleaned resume text
            resume_data: Optional parsed resume dict for engineered features

        Returns:
            Sparse feature matrix (1 row = this resume)
        """
        if self.vectorizer is None:
            raise RuntimeError("TF-IDF vectorizer not loaded")

        # Transform resume text → TF-IDF vector
        # transform() (not fit_transform!) because the vectorizer was already
        # fitted on the training data — we reuse that same vocabulary
        tfidf_vec = self.vectorizer.transform([resume_text])

        # Add engineered features if resume_data is available
        if resume_data and self.feature_info:
            eng_feat_names = self.feature_info.get('engineered_features', [])
            if eng_feat_names:
                # Build the same engineered features as in Phase 3
                eng_values = []
                text_lower = resume_text.lower()

                for feat_name in eng_feat_names:
                    if feat_name == 'word_count':
                        eng_values.append(len(resume_text.split()))
                    elif feat_name == 'char_count':
                        eng_values.append(len(resume_text))
                    elif feat_name == 'years_experience':
                        eng_values.append(resume_data.get('experience_years', 0))
                    elif feat_name == 'technical_skill_count':
                        eng_values.append(resume_data.get('technical_skill_count', 0))
                    elif feat_name == 'soft_skill_count':
                        eng_values.append(resume_data.get('soft_skill_count', 0))
                    elif feat_name.startswith('has_'):
                        skill = feat_name[4:].replace('_', ' ')
                        eng_values.append(1 if skill in text_lower else 0)
                    else:
                        eng_values.append(0)

                eng_matrix = sp.csr_matrix(np.array(eng_values).reshape(1, -1))
                # hstack: combine TF-IDF columns + engineered feature columns
                features = sp.hstack([tfidf_vec, eng_matrix])
                return features

        return tfidf_vec

    def predict(self, resume_text: str,
                resume_data: dict = None) -> dict:
        """
        Predict the single best career for a resume.

        Args:
            resume_text: Cleaned resume text
            resume_data: Optional parsed resume dict

        Returns:
            {
                'career':     'Data Scientist',
                'confidence': 87.3,
                'model_used': 'ensemble',
            }
        """
        if not self.models or self.label_encoder is None:
            return {'career': 'Unknown', 'confidence': 0.0, 'error': 'Models not loaded'}

        features = self._prepare_features(resume_text, resume_data)

        # Use ensemble if available, else best available model
        model_name = 'ensemble' if 'ensemble' in self.models else list(self.models.keys())[0]
        model = self.models[model_name]

        # predict() returns the class number
        pred_class = model.predict(features)[0]

        # predict_proba() returns confidence for EACH class
        # Shape: (1, num_classes) — one probability per career
        proba = model.predict_proba(features)[0]

        confidence = float(proba[pred_class]) * 100
        career = self.label_encoder.classes_[pred_class]

        return {
            'career':     career,
            'confidence': round(confidence, 1),
            'model_used': model_name,
        }

    def predict_top_n(self, resume_text: str,
                      resume_data: dict = None,
                      n: int = 5) -> list:
        """
        Predict the top N career recommendations with confidence scores.

        Args:
            resume_text: Cleaned resume text
            resume_data: Optional parsed resume dict
            n: Number of careers to return (default 5)

        Returns:
            List of dicts, sorted by confidence (highest first):
            [
                {'career': 'Data Scientist',      'confidence': 87.3},
                {'career': 'ML Engineer',          'confidence': 76.1},
                {'career': 'Data Analyst',         'confidence': 54.8},
                ...
            ]
        """
        if not self.models or self.label_encoder is None:
            return []

        features   = self._prepare_features(resume_text, resume_data)
        model_name = 'ensemble' if 'ensemble' in self.models else list(self.models.keys())[0]
        model      = self.models[model_name]

        proba = model.predict_proba(features)[0]  # All class probabilities

        # Get indices sorted by probability (highest first)
        # argsort() returns indices that would sort the array
        # [::-1] reverses (ascending → descending)
        sorted_indices = np.argsort(proba)[::-1]

        results = []
        for idx in sorted_indices[:n]:
            results.append({
                'career':     self.label_encoder.classes_[idx],
                'confidence': round(float(proba[idx]) * 100, 1),
                'rank':       len(results) + 1,
            })

        return results

    def get_career_skill_requirements(self, career: str) -> dict:
        """
        Return the typical skills, tools, and learning path for a career.

        This data is hardcoded from our CAREER_TEMPLATES in Phase 3.
        In a production system, this would come from a database.

        Args:
            career: Career name (must match label_encoder.classes_)

        Returns:
            Dict with skills, tools, learning_path, avg_salary, growth
        """
        # Career knowledge base — maps career to requirements
        career_knowledge = {
            "Data Scientist": {
                "core_skills":    ["Python", "Machine Learning", "Statistics",
                                   "SQL", "TensorFlow/PyTorch", "Data Visualization"],
                "tools":          ["Jupyter", "Pandas", "scikit-learn", "Tableau", "AWS"],
                "learning_path":  ["Python basics", "Statistics & Probability",
                                   "Machine Learning (Andrew Ng)", "Deep Learning",
                                   "Kaggle competitions", "Build portfolio"],
                "avg_salary_inr": "12-25 LPA",
                "growth":         "Very High",
                "companies":      ["Google", "Amazon", "Flipkart", "Swiggy", "CRED"],
            },
            "Software Engineer": {
                "core_skills":    ["DSA", "System Design", "Java/Python/C++",
                                   "Databases", "REST APIs", "Git"],
                "tools":          ["VS Code", "Docker", "AWS", "PostgreSQL", "Git"],
                "learning_path":  ["DSA (LeetCode)", "OOP concepts", "Database design",
                                   "System design", "Open source contribution"],
                "avg_salary_inr": "8-30 LPA",
                "growth":         "High",
                "companies":      ["Google", "Microsoft", "Infosys", "TCS", "Startups"],
            },
            "Machine Learning Engineer": {
                "core_skills":    ["Python", "PyTorch/TensorFlow", "MLOps",
                                   "Docker/Kubernetes", "Feature Engineering", "LLMs"],
                "tools":          ["MLflow", "Kubeflow", "AWS SageMaker", "FastAPI"],
                "learning_path":  ["Python", "ML fundamentals", "Deep Learning",
                                   "MLOps", "LangChain/LLMs", "Production ML systems"],
                "avg_salary_inr": "15-40 LPA",
                "growth":         "Extremely High",
                "companies":      ["OpenAI", "Google DeepMind", "Anthropic", "Sarvam AI"],
            },
            "Data Analyst": {
                "core_skills":    ["SQL", "Excel", "Tableau/Power BI",
                                   "Python/R", "Statistics", "Business Acumen"],
                "tools":          ["SQL", "Tableau", "Power BI", "Excel", "Google Analytics"],
                "learning_path":  ["Excel mastery", "SQL (Mode Analytics)",
                                   "Tableau/Power BI", "Python basics", "Business communication"],
                "avg_salary_inr": "5-15 LPA",
                "growth":         "High",
                "companies":      ["Deloitte", "KPMG", "Swiggy", "Meesho", "Banks"],
            },
            "Frontend Developer": {
                "core_skills":    ["HTML/CSS", "JavaScript", "React/Next.js",
                                   "TypeScript", "Responsive Design", "Git"],
                "tools":          ["VS Code", "Figma", "Webpack/Vite", "npm", "GitHub"],
                "learning_path":  ["HTML/CSS", "JavaScript (ES6+)", "React",
                                   "TypeScript", "Next.js", "Portfolio projects"],
                "avg_salary_inr": "6-20 LPA",
                "growth":         "High",
                "companies":      ["Startups", "Flipkart", "Razorpay", "Zepto"],
            },
            "DevOps Engineer": {
                "core_skills":    ["Linux", "Docker", "Kubernetes", "CI/CD",
                                   "Terraform", "AWS/Azure", "Python/Bash"],
                "tools":          ["Jenkins", "GitHub Actions", "Terraform", "Prometheus"],
                "learning_path":  ["Linux fundamentals", "Docker", "Kubernetes",
                                   "AWS certification", "Terraform", "CI/CD pipelines"],
                "avg_salary_inr": "10-30 LPA",
                "growth":         "Very High",
                "companies":      ["AWS", "Atlassian", "HashiCorp", "Zomato"],
            },
            "Cybersecurity Analyst": {
                "core_skills":    ["Network Security", "Penetration Testing",
                                   "SIEM", "Python", "Incident Response", "OWASP"],
                "tools":          ["Wireshark", "Metasploit", "Burp Suite", "Nmap", "Splunk"],
                "learning_path":  ["Networking basics", "CEH certification",
                                   "Ethical hacking", "CISSP", "SOC operations"],
                "avg_salary_inr": "8-25 LPA",
                "growth":         "Very High",
                "companies":      ["Palo Alto", "CrowdStrike", "TCS Cyber", "Banks"],
            },
        }

        # Return info for the requested career, or a generic response
        info = career_knowledge.get(career, {
            "core_skills":    ["Problem Solving", "Communication", "Domain Knowledge"],
            "tools":          ["Industry-standard tools"],
            "learning_path":  ["Build fundamentals", "Get certified", "Build projects"],
            "avg_salary_inr": "Varies by experience",
            "growth":         "Research the specific role",
            "companies":      ["Many options available"],
        })

        info['career'] = career
        return info


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6 — TRAINING SCRIPT (run directly)
# ════════════════════════════════════════════════════════════════════════════

def train_models():
    """Run the complete training pipeline."""
    X_train, X_test, y_train, y_test, label_encoder, feature_info = load_training_data()
    trained_models, results = train_all_models(X_train, X_test, y_train, y_test, label_encoder)
    save_models(trained_models, results)

    logger.info("\n" + "=" * 60)
    logger.info("PHASE 5 COMPLETE!")
    logger.info(f"Best accuracy: {max(results.values())*100:.1f}%")
    logger.info("Models saved to models/")
    logger.info("Ready for Phase 6 — ATS Engine")
    logger.info("=" * 60)

    return trained_models, results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s — %(levelname)s — %(message)s')
    train_models()