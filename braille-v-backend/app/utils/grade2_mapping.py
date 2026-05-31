"""
Braille-V Grade 2 Braille Mapping
Complete mapping tables for Grade 2 Braille contractions and indicators.
"""

# ─── Unicode Braille Block ───────────────────────────────────────────────────
# Braille characters live at U+2800..U+28FF.
# The codepoint offset encodes which dots are raised:
#   dot 1 = 0x01, dot 2 = 0x02, dot 3 = 0x04,
#   dot 4 = 0x08, dot 5 = 0x10, dot 6 = 0x20,
#   dot 7 = 0x40, dot 8 = 0x80   (8-dot Braille; we use 6-dot only)


def dots_to_unicode(dot_positions: list[int]) -> str:
    """Convert a list of raised dot numbers (1-6) to a Unicode Braille char."""
    offset = 0
    dot_bit = {1: 0x01, 2: 0x02, 3: 0x04, 4: 0x08, 5: 0x10, 6: 0x20}
    for d in dot_positions:
        offset |= dot_bit.get(d, 0)
    return chr(0x2800 + offset)


def unicode_to_dots(char: str) -> list[int]:
    """Convert a Unicode Braille character to a list of raised dot numbers."""
    offset = ord(char) - 0x2800
    dot_bit = {0x01: 1, 0x02: 2, 0x04: 3, 0x08: 4, 0x10: 5, 0x20: 6}
    return sorted(d for bit, d in dot_bit.items() if offset & bit)


# ─── Grade 1: Dot-pattern → letter / digit / punctuation ─────────────────────

GRADE1_MAP: dict[str, str] = {
    # Letters a-z
    dots_to_unicode([1]): "a",
    dots_to_unicode([1, 2]): "b",
    dots_to_unicode([1, 4]): "c",
    dots_to_unicode([1, 4, 5]): "d",
    dots_to_unicode([1, 5]): "e",
    dots_to_unicode([1, 2, 4]): "f",
    dots_to_unicode([1, 2, 4, 5]): "g",
    dots_to_unicode([1, 2, 5]): "h",
    dots_to_unicode([2, 4]): "i",
    dots_to_unicode([2, 4, 5]): "j",
    dots_to_unicode([1, 3]): "k",
    dots_to_unicode([1, 2, 3]): "l",
    dots_to_unicode([1, 3, 4]): "m",
    dots_to_unicode([1, 3, 4, 5]): "n",
    dots_to_unicode([1, 3, 5]): "o",
    dots_to_unicode([1, 2, 3, 4]): "p",
    dots_to_unicode([1, 2, 3, 4, 5]): "q",
    dots_to_unicode([1, 2, 3, 5]): "r",
    dots_to_unicode([2, 3, 4]): "s",
    dots_to_unicode([2, 3, 4, 5]): "t",
    dots_to_unicode([1, 3, 6]): "u",
    dots_to_unicode([1, 2, 3, 6]): "v",
    dots_to_unicode([2, 4, 5, 6]): "w",
    dots_to_unicode([1, 3, 4, 6]): "x",
    dots_to_unicode([1, 3, 4, 5, 6]): "y",
    dots_to_unicode([1, 3, 5, 6]): "z",
}

# Digits use the number indicator (⠼ dots 3-4-5-6) followed by
# the same patterns as letters a-j.
DIGIT_MAP: dict[str, str] = {
    dots_to_unicode([1]): "1",
    dots_to_unicode([1, 2]): "2",
    dots_to_unicode([1, 4]): "3",
    dots_to_unicode([1, 4, 5]): "4",
    dots_to_unicode([1, 5]): "5",
    dots_to_unicode([1, 2, 4]): "6",
    dots_to_unicode([1, 2, 4, 5]): "7",
    dots_to_unicode([1, 2, 5]): "8",
    dots_to_unicode([2, 4]): "9",
    dots_to_unicode([2, 4, 5]): "0",
}

# Punctuation
PUNCTUATION_MAP: dict[str, str] = {
    dots_to_unicode([2]): ",",
    dots_to_unicode([2, 3]): ";",
    dots_to_unicode([2, 5]): ":",
    dots_to_unicode([2, 5, 6]): ".",
    dots_to_unicode([2, 3, 5]): "!",
    dots_to_unicode([2, 3, 6]): "?",
    dots_to_unicode([3]): "'",
    dots_to_unicode([3, 5, 6]): "-",
}

# ─── Indicators ──────────────────────────────────────────────────────────────

CAPITAL_SIGN = dots_to_unicode([6])         # ⠠
NUMBER_SIGN = dots_to_unicode([3, 4, 5, 6])  # ⠼
LETTER_SIGN = dots_to_unicode([5, 6])        # ⠰ (terminates number mode)
SPACE = dots_to_unicode([])                   # ⠀ (empty cell = space)

# ─── Grade 2: Whole-word contractions ────────────────────────────────────────

GRADE2_WHOLE_WORD: dict[str, str] = {
    dots_to_unicode([1, 2]): "but",
    dots_to_unicode([1, 4]): "can",
    dots_to_unicode([1, 4, 5]): "do",
    dots_to_unicode([1, 5]): "every",
    dots_to_unicode([1, 2, 4]): "from",
    dots_to_unicode([1, 2, 4, 5]): "go",
    dots_to_unicode([1, 2, 5]): "have",
    dots_to_unicode([2, 4, 5]): "just",
    dots_to_unicode([1, 3]): "knowledge",
    dots_to_unicode([1, 2, 3]): "like",
    dots_to_unicode([1, 3, 4]): "more",
    dots_to_unicode([1, 3, 4, 5]): "not",
    dots_to_unicode([1, 2, 3, 4]): "people",
    dots_to_unicode([1, 2, 3, 4, 5]): "quite",
    dots_to_unicode([1, 2, 3, 5]): "rather",
    dots_to_unicode([2, 3, 4]): "so",
    dots_to_unicode([2, 3, 4, 5]): "that",
    dots_to_unicode([1, 3, 6]): "us",
    dots_to_unicode([1, 2, 3, 6]): "very",
    dots_to_unicode([2, 4, 5, 6]): "will",
    dots_to_unicode([1, 3, 4, 6]): "it",
    dots_to_unicode([1, 3, 4, 5, 6]): "you",
    dots_to_unicode([1, 3, 5, 6]): "as",
}

# ─── Grade 2: Multi-cell contractions ────────────────────────────────────────

GRADE2_MULTI_CELL: dict[str, str] = {
    # Two-cell whole-word signs
    dots_to_unicode([2, 3, 4, 6]) + dots_to_unicode([1, 5]): "the",
    dots_to_unicode([2, 3, 4, 6]) + dots_to_unicode([1, 2, 5]): "through",
    dots_to_unicode([2, 3, 4, 6]) + dots_to_unicode([2, 3, 4, 5]): "that",
    dots_to_unicode([2, 3, 4, 6]) + dots_to_unicode([2, 3, 4]): "this",
}

# ─── Grade 2: Short-form words ──────────────────────────────────────────────

GRADE2_SHORT_FORMS: dict[str, str] = {
    "ab": "about",
    "abv": "above",
    "ac": "according",
    "acr": "across",
    "af": "after",
    "afn": "afternoon",
    "afw": "afterward",
    "ag": "again",
    "agst": "against",
    "al": "also",
    "alm": "almost",
    "alr": "already",
    "alt": "altogether",
    "alth": "although",
    "alw": "always",
    "bec": "because",
    "bef": "before",
    "beh": "behind",
    "bel": "below",
    "ben": "beneath",
    "bes": "beside",
    "bet": "between",
    "bey": "beyond",
    "bl": "blind",
    "brl": "braille",
    "cd": "could",
    "ch": "children",
    "dcl": "declare",
    "dclg": "declaring",
    "ei": "either",
    "fr": "friend",
    "gd": "good",
    "grt": "great",
    "hm": "him",
    "hmf": "himself",
    "imm": "immediate",
    "lr": "letter",
    "ll": "little",
    "mch": "much",
    "mst": "must",
    "myf": "myself",
    "nec": "necessary",
    "nei": "neither",
    "o'c": "o'clock",
    "pd": "paid",
    "perh": "perhaps",
    "qk": "quick",
    "rcv": "receive",
    "rcvg": "receiving",
    "rjc": "rejoice",
    "rjcg": "rejoicing",
    "sd": "said",
    "sh": "shall",
    "shd": "should",
    "st": "still",
    "suc": "such",
    "td": "today",
    "tgr": "together",
    "tm": "tomorrow",
    "tn": "tonight",
    "wd": "would",
    "xs": "its",
    "xf": "itself",
    "yr": "your",
    "yrf": "yourself",
    "yrvs": "yourselves",
}

# ─── Grade 2: Group signs (part-word contractions) ───────────────────────────

GRADE2_GROUP_SIGNS: dict[str, str] = {
    dots_to_unicode([2, 3, 4, 6]): "th",
    dots_to_unicode([1, 4, 6]): "sh",
    dots_to_unicode([1, 6]): "ch",
    dots_to_unicode([1, 5, 6]): "wh",
    dots_to_unicode([1, 2, 6]): "gh",
    dots_to_unicode([1, 2, 4, 6]): "ed",
    dots_to_unicode([1, 2, 5, 6]): "er",
    dots_to_unicode([1, 4, 5, 6]): "ou",
    dots_to_unicode([1, 2, 4, 5, 6]): "ow",
    dots_to_unicode([3, 4, 6]): "ing",
    dots_to_unicode([3, 4]): "st",
    dots_to_unicode([1, 6]): "ch",
    dots_to_unicode([3, 4, 5]): "ar",
    dots_to_unicode([2, 6]): "en",
    dots_to_unicode([3, 5]): "in",
}
