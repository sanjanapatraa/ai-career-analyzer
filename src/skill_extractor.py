# src/skill_extractor.py
# ══════════════════════════════════════════════════════════════════════════
# SKILL EXTRACTOR — finds every skill in a resume using three strategies
#
# Strategy 1: PhraseMatcher (spaCy)
#   → Finds multi-word skills like "machine learning", "natural language processing"
#   → Fast and accurate for exact matches
#
# Strategy 2: Regex Pattern Matching
#   → Finds version-tagged skills like "Python 3.10", "React 18"
#   → Handles abbreviations: "ML", "NLP", "AI", "DS"
#
# Strategy 3: Section-aware extraction
#   → Parses the Skills section specifically
#   → Comma-separated and bullet-separated skill lists
#
# All three results are merged and deduplicated.
# ══════════════════════════════════════════════════════════════════════════

import re
import json
import os
import logging
from typing import Dict, List, Set, Optional, Tuple

import spacy
from spacy.matcher import PhraseMatcher   # For matching skill phrases

logger = logging.getLogger(__name__)

# ── Path setup ────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SKILL DATABASE LOADER
# ════════════════════════════════════════════════════════════════════════════

def load_skills_database() -> Dict[str, List[str]]:
    """
    Load the master skills database from config/skills_db.json.

    Returns:
        Dictionary with structure:
        {
            'programming_languages': ['python', 'java', ...],
            'web_technologies':      ['react', 'django', ...],
            'data_science_ml':       ['tensorflow', 'pandas', ...],
            ...
            'all_skills':            [...all combined...]
        }
    """
    db_path = os.path.join(CONFIG_DIR, 'skills_db.json')

    if not os.path.exists(db_path):
        logger.error(f"skills_db.json not found at {db_path}")
        return {'all_skills': []}

    with open(db_path, 'r', encoding='utf-8') as f:
        raw_db = json.load(f)

    # Flatten all technical skill categories into one list
    all_technical = []
    technical_by_category = {}

    for category, skills in raw_db.get('technical_skills', {}).items():
        # Lowercase all skills for consistent matching
        lower_skills = [s.lower() for s in skills]
        technical_by_category[category] = lower_skills
        all_technical.extend(lower_skills)

    soft_skills = [s.lower() for s in raw_db.get('soft_skills', [])]

    result = {
        **technical_by_category,          # All category-specific lists
        'soft_skills': soft_skills,        # Soft skills list
        'all_skills':  list(set(all_technical + soft_skills)),  # Combined unique
    }

    logger.info(f"Loaded {len(result['all_skills'])} unique skills from database")
    return result


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — SPACY PHRASE MATCHER SETUP
# ════════════════════════════════════════════════════════════════════════════

class SkillExtractor:
    """
    Main skill extraction class.

    We make this a class (instead of plain functions) because:
    - The spaCy model and PhraseMatcher are HEAVY to load
    - Loading takes 3-5 seconds
    - With a class, we load ONCE and reuse the same object
    - This is called the "singleton" design pattern

    Usage:
        extractor = SkillExtractor()          # Load once
        skills = extractor.extract(text)      # Use many times
    """

    def __init__(self):
        """
        Initialize the skill extractor.
        This runs ONCE when we create the object.
        It loads spaCy and builds the PhraseMatcher.
        """
        logger.info("Initializing SkillExtractor...")

        # Load skills database
        self.skills_db = load_skills_database()

        # Load spaCy NLP model
        # We disable components we don't need to make it faster
        # We only need: tokenizer (built-in), lemmatizer, tagger
        # We do NOT need: ner (named entity recognition), parser (dependency parsing)
        try:
            self.nlp = spacy.load(
                "en_core_web_sm",
            
                disable=["ner", "parser"]  # Disable unused components for speed
            )
            # Increase max text length (resumes can be long)
            self.nlp.max_length = 2_000_000
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.error("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None

        # Build the PhraseMatcher with all known skills
        self.matcher = self._build_phrase_matcher()

        # Also build a quick-lookup set for exact matching
        # Sets have O(1) lookup — much faster than searching a list
        self.all_skills_set = set(self.skills_db.get('all_skills', []))

        logger.info(
            f"SkillExtractor ready: {len(self.all_skills_set)} skills indexed"
        )

    def _build_phrase_matcher(self) -> Optional[PhraseMatcher]:
        """
        Build a spaCy PhraseMatcher loaded with all known skills.

        What is PhraseMatcher?
        It's like a very fast, smart find-and-replace.
        You give it a list of phrases to search for.
        You give it a document of text.
        It tells you exactly where each phrase appears.

        Why PhraseMatcher instead of regex?
        → PhraseMatcher uses spaCy's tokenization, so it handles
          "Machine Learning" and "machine learning" and "MACHINE LEARNING"
          all as the same match (case-insensitive via LOWER attribute).
        → Much faster than regex for thousands of patterns.

        Returns:
            PhraseMatcher object, or None if spaCy not available
        """
        if self.nlp is None:
            return None

        # PhraseMatcher(vocab, attr="LOWER") means:
        # - vocab: the spaCy vocabulary (knows all words)
        # - attr="LOWER": match on lowercase version of words
        #   This makes matching case-insensitive!
        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        all_skills = self.skills_db.get('all_skills', [])

        # Convert each skill string into a spaCy Doc object
        # PhraseMatcher needs Doc objects, not plain strings
        # nlp.pipe() processes many texts at once (faster than one-by-one)
        skill_docs = list(self.nlp.pipe(all_skills))

        # Add all skill patterns to the matcher under the label "SKILL"
        # The label is just a name we give this group of patterns
        matcher.add("SKILL", skill_docs)

        logger.info(f"PhraseMatcher built with {len(skill_docs)} skill patterns")
        return matcher

    # ────────────────────────────────────────────────────────────────────────
    # STRATEGY 1: PhraseMatcher extraction
    # ────────────────────────────────────────────────────────────────────────

    def extract_with_phrase_matcher(self, text: str) -> Set[str]:
        """
        Use spaCy PhraseMatcher to find skills in text.

        Args:
            text: Resume text (raw or cleaned)

        Returns:
            Set of skill strings found (lowercase, deduplicated)

        How PhraseMatcher works:
        1. spaCy tokenizes the text into words
        2. PhraseMatcher slides a window over the tokens
        3. It checks if the window matches any skill phrase
        4. If yes, it records the start/end position
        5. We extract the matched text from those positions
        """
        if self.nlp is None or self.matcher is None:
            return set()

        # Limit text length to avoid memory issues
        # (Most resumes are well under 10,000 characters)
        text_limited = text[:10_000]

        # Process the text with spaCy to create a Doc object
        # A Doc is spaCy's internal representation: tokens with metadata
        doc = self.nlp(text_limited.lower())

        # Run the PhraseMatcher on the document
        # matches is a list of (match_id, start_token, end_token) tuples
        matches = self.matcher(doc)

        found_skills = set()
        for match_id, start, end in matches:
            # doc[start:end] is the matched "span" (a slice of tokens)
            # .text gives us the actual text of the span
            skill_text = doc[start:end].text.lower().strip()
            if skill_text:
                found_skills.add(skill_text)

        return found_skills

    # ────────────────────────────────────────────────────────────────────────
    # STRATEGY 2: Regex pattern matching
    # ────────────────────────────────────────────────────────────────────────

    def extract_with_regex(self, text: str) -> Set[str]:
        """
        Use regex patterns to find skills that PhraseMatcher might miss.

        Handles:
        - Skills with version numbers: "Python 3.10", "React 18.2"
        - Abbreviations: "ML", "NLP", "AI", "CV", "DL"
        - Skills with special chars: "C++", "C#", ".NET", "Node.js"

        Args:
            text: Resume text

        Returns:
            Set of skill strings found
        """
        found = set()
        text_lower = text.lower()

        # ── Abbreviations and special-character skills ─────────────────────
        # These are hard for the phrase matcher because they're very short
        abbreviations = {
            r'\bml\b':           'machine learning',
            r'\bnlp\b':          'natural language processing',
            r'\bcv\b':           'computer vision',
            r'\bai\b':           'artificial intelligence',
            r'\bdl\b':           'deep learning',
            r'\brl\b':           'reinforcement learning',
            r'\bllm\b':          'large language models',
            r'\brag\b':          'retrieval augmented generation',
            r'\bapi\b':          'api development',
            r'\bci/cd\b':        'ci/cd',
            r'\bcicd\b':         'ci/cd',
            r'\baws\b':          'aws',
            r'\bgcp\b':          'google cloud',
            r'\bc\+\+':          'c++',
            r'\bc#':             'c#',
            r'\.net\b':          '.net',
            r'\bnode\.js\b':     'node.js',
            r'\breact\.js\b':    'react',
            r'\bvue\.js\b':      'vue',
            r'\bnext\.js\b':     'next.js',
            r'\bnuxt\.js\b':     'nuxt',
            r'\bexpress\.js\b':  'express',
            r'\bios\b':          'ios development',
            r'\bsql\b':          'sql',
            r'\bnosql\b':        'nosql',
            r'\borm\b':          'orm',
            r'\bsdlc\b':         'sdlc',
            r'\boop\b':          'object oriented programming',
            r'\brest\b':         'rest api',
            r'\bgrpc\b':         'grpc',
            r'\bgit\b':          'git',
        }

        for pattern, canonical_name in abbreviations.items():
            if re.search(pattern, text_lower):
                found.add(canonical_name)

        # ── Skills with version numbers ────────────────────────────────────
        # Pattern: word followed by version number like "Python 3", "React 18"
        versioned = re.findall(
            r'\b(python|java|react|angular|vue|tensorflow|pytorch|django|flask|'
            r'kubernetes|docker|postgresql|mysql|mongodb|redis)\s+\d+',
            text_lower
        )
        for skill in versioned:
            found.add(skill.strip())

        return found

    # ────────────────────────────────────────────────────────────────────────
    # STRATEGY 3: Skills section parsing
    # ────────────────────────────────────────────────────────────────────────

    def extract_from_skills_section(self,
                                    sections: Dict[str, str]) -> Set[str]:
        """
        Parse the dedicated Skills section of the resume.

        The Skills section often has comma-separated or bullet-separated lists.
        This strategy directly parses those lists.

        Args:
            sections: Dictionary from split_resume_into_sections()
                      e.g., {'skills': 'Python, Java, SQL, TensorFlow...'}

        Returns:
            Set of skill strings found in the skills section
        """
        skills_text = sections.get('skills', '')
        if not skills_text:
            return set()

        found = set()
        lines = skills_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove common prefixes like "Languages:", "Frameworks:", "Tools:"
            # These are sub-headers within the skills section
            # Pattern: "Word:" at the start of a line
            line = re.sub(r'^[\w\s/]+:\s*', '', line)

            # Skills are separated by commas, bullets, pipes, or semicolons
            # re.split() splits on any of these characters
            separators = r'[,|;•·\t]|\s{2,}'  # comma, pipe, semicolon, bullet, tab, 2+ spaces
            tokens = re.split(separators, line)

            for token in tokens:
                # Clean the token
                token = token.strip().strip('•-*·').strip()

                # Skip empty tokens and very long ones (probably sentences, not skills)
                if not token or len(token) < 2 or len(token) > 40:
                    continue

                token_lower = token.lower()

                # Check if this token matches any known skill
                if token_lower in self.all_skills_set:
                    found.add(token_lower)
                # Also check partial match (for compound skills)
                elif any(skill in token_lower for skill in self.all_skills_set
                         if len(skill) > 4):   # Only check skills 5+ chars long
                    # Find the best match
                    for skill in self.all_skills_set:
                        if len(skill) > 4 and skill in token_lower:
                            found.add(skill)

        return found

    # ────────────────────────────────────────────────────────────────────────
    # MAIN EXTRACTION FUNCTION — combines all three strategies
    # ────────────────────────────────────────────────────────────────────────

    def extract(self, text: str,
                sections: Optional[Dict[str, str]] = None) -> Dict:
        """
        Extract all skills from resume text using all three strategies.

        This is the MAIN method called by the rest of the app.

        Args:
            text:     Full resume text (raw or cleaned)
            sections: Optional dict from split_resume_into_sections()
                      If provided, we also parse the skills section directly.

        Returns:
            Dictionary with structure:
            {
                'all_skills':      ['python', 'sql', 'machine learning', ...],
                'by_category':     {
                    'programming_languages': ['python', 'java'],
                    'data_science_ml':       ['tensorflow', 'pandas'],
                    ...
                },
                'technical_skills': ['python', 'tensorflow', ...],
                'soft_skills':      ['communication', 'leadership'],
                'total_count':      25,
                'match_sources':    {'phrase_matcher': 18, 'regex': 5, 'section': 12}
            }
        """
        logger.info("Extracting skills...")

        # ── Run all three strategies ───────────────────────────────────────
        phrase_skills  = self.extract_with_phrase_matcher(text)
        regex_skills   = self.extract_with_regex(text)
        section_skills = (self.extract_from_skills_section(sections)
                         if sections else set())

        # ── Merge all found skills ─────────────────────────────────────────
        # Python set union (|) combines all three sets, removing duplicates
        all_found = phrase_skills | regex_skills | section_skills

        # ── Categorize the found skills ────────────────────────────────────
        by_category = {}
        technical_skills = []
        soft_skills_found = []

        soft_skills_set = set(self.skills_db.get('soft_skills', []))

        for category, category_skills in self.skills_db.items():
            if category in ('all_skills', 'soft_skills'):
                continue   # Skip meta-categories

            # Find which skills from this category appear in our found set
            matched = [
                skill for skill in category_skills
                if skill in all_found
            ]

            if matched:
                by_category[category] = matched
                technical_skills.extend(matched)

        # Separate soft skills
        soft_skills_found = [s for s in all_found if s in soft_skills_set]

        # ── Build final result ─────────────────────────────────────────────
        # Convert set → sorted list for consistent output
        all_skills_list = sorted(list(all_found))

        result = {
            'all_skills':       all_skills_list,
            'by_category':      by_category,
            'technical_skills': sorted(list(set(technical_skills))),
            'soft_skills':      sorted(soft_skills_found),
            'total_count':      len(all_skills_list),
            'match_sources': {
                'phrase_matcher': len(phrase_skills),
                'regex':          len(regex_skills),
                'section_parse':  len(section_skills),
            }
        }

        logger.info(f"Extracted {result['total_count']} skills total")
        logger.info(f"  Technical: {len(result['technical_skills'])}, "
                    f"Soft: {len(result['soft_skills'])}")

        return result


# ── Module-level singleton ──────────────────────────────────────────────────
# We create ONE instance at module level so spaCy loads only once.
# Any file that imports this module reuses the same loaded model.
# This saves 3-5 seconds on every request.
_extractor_instance: Optional[SkillExtractor] = None


def get_skill_extractor() -> SkillExtractor:
    """
    Get the singleton SkillExtractor instance.
    Creates it on first call, returns cached instance on subsequent calls.

    This is called a "lazy singleton" — we only create it when first needed.
    """
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = SkillExtractor()
    return _extractor_instance


def extract_skills(text: str,
                   sections: Optional[Dict] = None) -> Dict:
    """
    Convenience function — the main API for skill extraction.

    This is what the Streamlit app calls.
    It handles getting the singleton and calling extract().

    Args:
        text:     Resume text
        sections: Optional sections dict

    Returns:
        Skills dictionary (see SkillExtractor.extract() for structure)
    """
    extractor = get_skill_extractor()
    return extractor.extract(text, sections)


# ── Quick test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    test_text = """
    John Smith — Data Scientist
    Skills: Python, TensorFlow, PyTorch, SQL, Machine Learning, NLP,
    Docker, AWS, Pandas, NumPy, scikit-learn, Tableau, Git
    Experience: 4 years building ML models and deep learning systems.
    Led team using Agile methodology and strong communication skills.
    """

    print("Testing skill extractor...")
    result = extract_skills(test_text)

    print(f"\nTotal skills found: {result['total_count']}")
    print(f"All skills: {result['all_skills']}")
    print(f"\nBy category:")
    for cat, skills in result['by_category'].items():
        print(f"  {cat}: {skills}")
    print(f"\nSoft skills: {result['soft_skills']}")
    print(f"\nMatch sources: {result['match_sources']}")