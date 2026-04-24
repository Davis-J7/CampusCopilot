"""
chatbot.py
----------
NLP-based chatbot using spaCy for Semantic Similarity.

HOW IT WORKS:
  1. We load a medium-sized spaCy model ('en_core_web_md') which contains
     pre-trained word vectors.
  2. Each intent is defined by a set of "anchor" keywords. These are 
     converted into spaCy Doc objects.
  3. When a user query arrives, we convert it into a Doc and calculate its
     semantic similarity against each intent's anchor Doc.
  4. The intent with the highest similarity score wins.

Why spaCy?
  - Semantic Understanding: It knows that "money" is related to "fees" even
    if the word "fees" isn't used.
  - No Training Needed: We use the pre-trained vectors to get "intelligent"
    matching out of the box.
"""

from typing import Callable, Dict, List, Set, Optional
from .algorithms import find_closest_keyword

# -----------------------------------------------------------------------------
# INTENT REGISTRY
# -----------------------------------------------------------------------------
INTENT_KEYWORDS: Dict[str, str] = {
    "events":        "event events fest workshop hackathon competition contest programs",
    "fees":          "fee fees tuition payment academic dues",
    "schedule":      "schedule exam exams timetable class classes test tests",
    "students":      "student students enrolled enrollment pending",
    "requirements":  "requirements prerequisite join criteria can i join need for joining",
    "map":           "map location where campus directions building",
    "optimize":      "optimize optimising best maximum plan recommend suggest",
    "help":          "help commands menu options instructions",
    "quit":          "quit exit bye goodbye stop close",
}

def classify_intent(query: str) -> str:
    """
    Classifies intent using a mix of exact keyword matching and fuzzy matching (Levenshtein).
    """
    query = query.lower().strip()
    if not query:
        return "unknown"

    words = query.split()
    
    # 1. PRIORITY: Check for 'requirements' specifically to avoid it being overshadowed by 'events'
    # if the query contains an event name (like "AI Workshop").
    req_keywords = INTENT_KEYWORDS["requirements"].split()
    if any(word in req_keywords for word in words):
        return "requirements"
    
    # Fuzzy check for "requirements" typos specifically
    for word in words:
        if len(word) >= 8:
            dist = find_closest_keyword(word, req_keywords, max_distance=2)
            if dist:
                return "requirements"

    # 2. Exact matching (check all words in query against all keyword sets)
    for intent, keywords in INTENT_KEYWORDS.items():
        keyword_list = keywords.split()
        if any(word in keyword_list for word in words):
            return intent

    # 3. General Fuzzy matching (Levenshtein)
    # We flatten all keywords into a single list to find the best match.
    all_keywords = []
    kw_to_intent = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords.split():
            all_keywords.append(kw)
            kw_to_intent[kw] = intent

    for word in words:
        # We only fuzzy match if the word is long enough to avoid false positives
        if len(word) < 4:
            continue
            
        best_kw = find_closest_keyword(word, all_keywords, max_distance=2)
        if best_kw:
            return kw_to_intent[best_kw]

    return "unknown"


class Chatbot:
    def __init__(self, handlers: Dict[str, Callable[[str], str]]) -> None:
        self.handlers = handlers

    def handle(self, query: str) -> str:
        intent = classify_intent(query)
        handler = self.handlers.get(intent, self._unknown)
        return handler(query)

    @staticmethod
    def _unknown(query: str = "") -> str:
        return (
            "I'm not quite sure I understood. Are you asking about:\n"
            "  events | fees | schedule | students | map | optimize | help"
        )
