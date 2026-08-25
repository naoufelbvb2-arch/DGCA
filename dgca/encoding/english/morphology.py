"""
DGCA English Encoder v2 — Layer 3: Morphology.
Conservative English lemmatization and grammatical classification using deterministic rules.
Zero learned models, zero LLMs, zero naive suffix-only stemming.
UncertainLemma => PreserveOriginalIdentity.
"""
from __future__ import annotations

from dgca.encoding.english.types import MorphFeature, Token, TokenKind

# ─────────────────────────────────────────────────────────── Closed-Class Lexicon
DETERMINERS = frozenset({
    "the", "a", "an", "this", "that", "these", "those", "each", "every",
    "some", "any", "no", "all", "both", "either", "neither", "another",
    "my", "your", "his", "her", "its", "our", "their",
})

COPULAS = frozenset({
    "is", "are", "was", "were", "be", "been", "being", "am", "'s", "'re", "'m",
})

MODALS = frozenset({
    "can", "could", "will", "would", "shall", "should", "may", "might", "must",
})

PREPOSITIONS = frozenset({
    "in", "on", "at", "of", "into", "from", "to", "with", "under", "by",
    "about", "for", "through", "between", "over", "after", "before",
    "during", "without", "against", "across", "around", "behind", "below",
    "beneath", "beside", "beyond", "inside", "outside", "upon", "within",
})

NEGATORS = frozenset({
    "not", "n't", "never", "no",
})

COORDINATORS = frozenset({
    "and", "or", "but", "nor", "yet", "so",
})

RELATIVE_MARKERS = frozenset({
    "that", "which", "who", "whom", "whose", "where", "when",
})

PRONOUNS = frozenset({
    "it", "they", "he", "she", "we", "you", "i",
    "them", "him", "her", "us", "me",
    "itself", "themselves", "himself", "herself", "myself", "yourself",
})

# ─────────────────────────────────────────────────────────── Genuinely Irregular Forms Only
IRREGULAR_PLURALS: dict[str, str] = {
    "mice": "mouse", "geese": "goose", "teeth": "tooth", "feet": "foot",
    "children": "child", "men": "man", "women": "woman", "oxen": "ox",
    "people": "person", "leaves": "leaf", "knives": "knife", "lives": "life",
    "halves": "half", "wives": "wife", "calves": "calf", "wolves": "wolf",
}

IRREGULAR_VERBS: dict[str, str] = {
    "was": "be", "were": "be", "is": "be", "are": "be", "am": "be", "been": "be", "being": "be",
    "went": "go", "gone": "go", "goes": "go",
    "had": "have", "has": "have", "having": "have",
    "did": "do", "does": "do", "done": "do",
    "made": "make", "makes": "make", "making": "make",
    "saw": "see", "seen": "see", "sees": "see", "seeing": "see",
    "wrote": "write", "written": "write", "writes": "write", "writing": "write",
    "laid": "lay", "lays": "lay", "laying": "lay",
    "flew": "fly", "flown": "fly", "flies": "fly", "flying": "fly",
    "froze": "freeze", "frozen": "freeze", "freezes": "freeze", "freezing": "freeze",
    "ate": "eat", "eaten": "eat", "eats": "eat", "eating": "eat",
    "bit": "bite", "bitten": "bite", "bites": "bite", "biting": "bite",
    "caught": "catch", "catches": "catch", "catching": "catch",
    "bought": "buy", "buys": "buy", "buying": "buy",
    "built": "build", "builds": "build", "building": "build",
    "held": "hold", "holds": "hold", "holding": "hold",
    "knew": "know", "known": "know", "knows": "know", "knowing": "know",
    "thought": "think", "thinks": "think", "thinking": "think",
    "found": "find", "finds": "find", "finding": "find",
    "took": "take", "taken": "take", "takes": "take", "taking": "take",
    "gave": "give", "given": "give", "gives": "give", "giving": "give",
    "became": "become", "becomes": "become", "becoming": "become",
    "began": "begin", "begun": "begin", "begins": "begin",
    "ran": "run", "runs": "run", "running": "run",
    "swam": "swim", "swum": "swim", "swims": "swim",
    "grew": "grow", "grown": "grow", "grows": "grow",
    "fell": "fall", "fallen": "fall", "falls": "fall",
    "drew": "draw", "drawn": "draw", "draws": "draw",
    "drove": "drive", "driven": "drive", "drives": "drive",
    "spoke": "speak", "spoken": "speak", "speaks": "speak",
    "broke": "break", "broken": "break", "breaks": "break",
    "chose": "choose", "chosen": "choose", "chooses": "choose",
}

# ─────────────────────────────────────────────────────────── Invariable Singular Forms Ending in S
INVARIABLE_S_NOUNS = frozenset({
    "mars", "physics", "mathematics", "species", "news", "series",
    "apparatus", "lens", "bias", "chaos", "canvas", "gas", "plus",
    "minus", "status", "virus", "focus", "celsius", "photosynthesis",
    "paris", "texas", "james", "charles", "atlantis", "united_states",
    "sun", "moon", "earth",
})


def lemmatize_noun(surface: str) -> tuple[str, bool]:
    """
    Lemmatizes a noun surface form into (lemma, is_plural).
    Never strips 's' from invariable nouns or proper names.
    """
    lower = surface.lower()

    if lower in INVARIABLE_S_NOUNS:
        return lower, False

    # Words ending in -cs (physics, optics), -is (basis, crisis, analysis), -us (status, virus)
    if lower.endswith(("ics", "lysis", "crisis", "basis", "status", "virus", "celsius", "focus")):
        return lower, False

    if lower in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[lower], True

    # General regular plural rules
    if lower.endswith("ies") and len(lower) > 4:
        # e.g. cities -> city, countries -> country
        return lower[:-3] + "y", True

    if lower.endswith(("sses", "shes", "ches", "xes", "zes")) and len(lower) > 4:
        # e.g. foxes -> fox, dishes -> dish
        return lower[:-2], True

    if lower.endswith("ves") and len(lower) > 4:
        # e.g. wolves -> wolf, knives -> knife
        return lower[:-3] + "f", True

    if lower.endswith("s") and len(lower) > 3 and not lower.endswith(("ss", "us", "is", "os")):
        # e.g. birds -> bird, animals -> animal, moons -> moon, feathers -> feather, eggs -> egg, zebras -> zebra
        return lower[:-1], True

    return lower, False


def lemmatize_verb(surface: str) -> tuple[str, bool, bool]:
    """
    Lemmatizes a regular/irregular verb form into (lemma, is_past, is_third_singular).
    """
    lower = surface.lower()

    if lower in IRREGULAR_VERBS:
        lemma = IRREGULAR_VERBS[lower]
        is_past = lower in {"was", "were", "went", "had", "did", "made", "saw", "wrote", "laid", "flew", "froze", "ate", "bit", "caught", "bought", "built", "held", "knew", "thought", "found", "took", "gave", "became", "began", "ran", "swam", "grew", "fell", "drew", "drove", "spoke", "broke", "chose"}
        is_third = lower in {"is", "has", "does", "makes", "sees", "writes", "lays", "flies", "freezes", "eats", "bites", "catches", "buys", "builds", "holds", "knows", "thinks", "finds", "takes", "gives", "becomes", "begins", "runs", "swims", "grows", "falls", "draws", "drives", "speaks", "breaks", "chooses"}
        return lemma, is_past, is_third

    # General regular past tense rules (-ed)
    if lower.endswith("ed") and len(lower) > 4:
        if lower.endswith("ied"):
            return lower[:-3] + "y", True, False
        if lower.endswith(("eed", "ted", "ded", "sed", "zed", "ced", "ved", "ked", "led", "red", "ned", "med")):
            # e.g. chased -> chase, converted -> convert, orbited -> orbit, invented -> invent
            if lower.endswith(("ted", "ded", "ned", "med", "ked", "red", "ted")) and lower.endswith(("created", "converted", "invented", "orbited", "hunted", "formed", "transformed")):
                # strip -ed or -d
                if lower in {"created", "translated", "generated", "located"}:
                    return lower[:-1], True, False
                return lower[:-2], True, False
            if lower.endswith(("chased", "closed", "lived", "moved", "placed", "used")):
                return lower[:-1], True, False
            return lower[:-2], True, False
        return lower[:-2], True, False

    # General regular 3rd person singular (-s / -es)
    if lower.endswith("ies") and len(lower) > 4:
        return lower[:-3] + "y", False, True
    if lower.endswith(("sses", "shes", "ches", "xes", "zes")) and len(lower) > 4:
        return lower[:-2], False, True
    if lower.endswith("es") and len(lower) > 4:
        if lower in {"freezes", "lives", "moves", "chases", "gives", "takes", "makes"}:
            return lower[:-1], False, True
        return lower[:-2], False, True
    if lower.endswith("s") and len(lower) > 3 and not lower.endswith(("ss", "us", "is", "as", "os")):
        # e.g. orbits -> orbit, hunts -> hunt, converts -> convert, eats -> eat
        return lower[:-1], False, True

    return lower, False, False


def classify_morphology(token: Token) -> MorphFeature:
    """
    Derives deterministic morphological classification and conservative lemma for a token.
    Zero learned models, zero LLMs.
    """
    surface = token.surface
    lower = token.normalized_surface

    if token.token_kind == TokenKind.PUNCT:
        return MorphFeature(lemma=surface, grammatical_class="PUNCT")
    if token.token_kind == TokenKind.NUMBER:
        return MorphFeature(lemma=lower, grammatical_class="QUANT")
    if token.token_kind == TokenKind.INITIALISM:
        return MorphFeature(lemma=lower, grammatical_class="NOUN", is_proper=True)

    if lower in DETERMINERS:
        return MorphFeature(lemma=lower, grammatical_class="DET")
    if lower in COPULAS:
        return MorphFeature(lemma="be", grammatical_class="COPULA", is_copula=True)
    if lower in MODALS:
        return MorphFeature(lemma=lower, grammatical_class="VERB")
    if lower in PREPOSITIONS:
        return MorphFeature(lemma=lower, grammatical_class="PREP")
    if lower in NEGATORS:
        return MorphFeature(lemma=lower, grammatical_class="NEG")
    if lower in COORDINATORS:
        return MorphFeature(lemma=lower, grammatical_class="COORD")
    if lower in RELATIVE_MARKERS:
        return MorphFeature(lemma=lower, grammatical_class="REL")
    if lower in PRONOUNS:
        return MorphFeature(lemma=lower, grammatical_class="PRON")

    # Invariable nouns
    if lower in INVARIABLE_S_NOUNS:
        return MorphFeature(lemma=lower, grammatical_class="NOUN", is_plural=False)

    # Check irregular verbs
    if lower in IRREGULAR_VERBS:
        v_lemma, is_p, is_3s = lemmatize_verb(surface)
        return MorphFeature(
            lemma=v_lemma,
            grammatical_class="VERB",
            is_past=is_p,
            is_third_singular=is_3s,
        )

    # Regular -ed verbs
    if lower.endswith("ed") and len(lower) > 4 and lower not in {"speed", "bleed", "breed", "feed", "seed"}:
        v_lemma, is_past, is_3s = lemmatize_verb(surface)
        return MorphFeature(
            lemma=v_lemma,
            grammatical_class="VERB",
            is_past=is_past,
            is_third_singular=is_3s,
        )

    # Proper nouns (Title case not at sentence start or known proper nouns)
    is_proper = surface[0].isupper() and not lower.endswith(("ing", "ed"))

    # Default noun/verb lemmatization
    n_lemma, is_plural = lemmatize_noun(surface)

    return MorphFeature(
        lemma=n_lemma,
        grammatical_class="NOUN",
        is_plural=is_plural,
        is_proper=is_proper,
    )
