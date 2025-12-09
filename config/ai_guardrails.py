import re

# ---------------------------------------------------------
# Forbidden keyword sets
# ---------------------------------------------------------

FORBIDDEN_KEYWORDS = [
    # Personal identity / location
    "address", "home address", "donde vives", "dónde vives", "where do you live",
    "location", "ubicación", "city", "ciudad", "state ", "estado", "country", "país",
    "live", "living",

    # Age / DOB
    "how old are you", "what is your age", "birthday", "date of birth",
    "edad", "cuántos años tienes", "cumpleaños", "fecha de nacimiento",

    # Family / Relationships
    "family", "wife", "spouse", "married", "kids", "children", "parents",
    "familia", "esposa", "pareja", "hijos", "niños", "padres", "hermanos",

    # Contact
    "phone", "phone number", "email", "contact info",
    "teléfono", "número", "correo", "correo electrónico", "contacto",

    # Legal IDs
    "ssn", "social security", "seguro social",
    "driver license", "passport", "licencia", "pasaporte",

    # Financial
    "salary", "how much do you earn", "income",
    "dinero", "sueldo", "cuánto ganas",

    # Religion / Politics (fully blocked)
    "religion", "religión",
    "politics", "política",
    "beliefs", "creencias",

    # Physical attributes
    "appearance", "height", "weight",
    "apariencia", "altura", "peso",

    # Birth origin / nationality
    "where are you from", "de dónde eres",
]

# ---------------------------------------------------------
# Forbidden intent patterns (more flexible than keywords)
# ---------------------------------------------------------

FORBIDDEN_INTENT_PHRASES = [
    # Personal life probing
    "personal life", "vida personal",
    "about your family", "sobre tu familia",
    "are you married", "estás casado",
    "do you have kids", "tienes hijos",

    # Personal whereabouts
    "where do you live", "donde vives",

    # Money-related
    "how much do you make", "how much money do you make",
    "cuánto dinero haces", "cuánto ganas",
]

# ---------------------------------------------------------
# Allowed follow-up phrases (always allowed for experience/skills)
# ---------------------------------------------------------

SAFE_FOLLOW_UPS = [
    "what else",
    "can you elaborate",
    "tell me more",
    "before that",
    "after that",
    "what did you do there",
    "what did you work on",
    "expand",
    "continue",
    "follow up",
]

def is_forbidden_message(text: str) -> bool:
    """
    Returns True if message includes blocked content.
    """

    lowered = text.lower().strip()

    # Allow safe follow-ups
    for phrase in SAFE_FOLLOW_UPS:
        if lowered.startswith(phrase):
            return False

    # Check forbidden intent phrases
    for intent in FORBIDDEN_INTENT_PHRASES:
        if intent in lowered:
            return True

    # Check keyword-based rules (with word-boundaries)
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{re.escape(keyword)}\b"
        if re.search(pattern, lowered):
            return True

    return False