"""
Braille-V Braille → English Conversion Service
Converts dot patterns to Unicode Braille, then decodes to English
with Grade 1 and Grade 2 support.
"""

from app.utils.grade2_mapping import (
    CAPITAL_SIGN,
    DIGIT_MAP,
    GRADE1_MAP,
    GRADE2_GROUP_SIGNS,
    GRADE2_MULTI_CELL,
    GRADE2_SHORT_FORMS,
    GRADE2_WHOLE_WORD,
    LETTER_SIGN,
    NUMBER_SIGN,
    PUNCTUATION_MAP,
    SPACE,
    dots_to_unicode,
)


class BrailleToEnglish:
    """Convert Braille cells (dot patterns) → Unicode Braille → English text."""

    def __init__(self):
        # Build combined lookup for decoding
        self._grade1 = {**GRADE1_MAP, **PUNCTUATION_MAP}

    # ── public API ───────────────────────────────────────────────────────

    def convert_to_unicode(self, cells: list[dict]) -> str:
        """
        Convert a list of cell dicts (with 'dot_positions') to
        a Unicode Braille string.
        """
        unicode_chars: list[str] = []
        for cell in cells:
            dp = cell.get("dot_positions", [])
            if not dp:
                unicode_chars.append(SPACE)
            else:
                unicode_chars.append(dots_to_unicode(dp))
        return "".join(unicode_chars)

    def convert_to_english(self, unicode_braille: str) -> str:
        """
        Decode a Unicode Braille string to English.
        Handles: capital signs, number signs, Grade 1, Grade 2 contractions.
        """
        result: list[str] = []
        i = 0
        capitalize_next = False
        number_mode = False

        while i < len(unicode_braille):
            char = unicode_braille[i]

            # ── Indicators ───────────────────────────────────────────
            if char == CAPITAL_SIGN:
                capitalize_next = True
                i += 1
                continue

            if char == NUMBER_SIGN:
                number_mode = True
                i += 1
                continue

            if char == LETTER_SIGN:
                number_mode = False
                i += 1
                continue

            if char == SPACE:
                result.append(" ")
                number_mode = False
                i += 1
                continue

            # ── Multi-cell contractions (Grade 2) ────────────────────
            matched_multi = False
            if i + 1 < len(unicode_braille):
                two_char = unicode_braille[i : i + 2]
                if two_char in GRADE2_MULTI_CELL:
                    word = GRADE2_MULTI_CELL[two_char]
                    if capitalize_next:
                        word = word.capitalize()
                        capitalize_next = False
                    result.append(word)
                    i += 2
                    matched_multi = True

            if matched_multi:
                continue

            # ── Number mode ──────────────────────────────────────────
            if number_mode and char in DIGIT_MAP:
                result.append(DIGIT_MAP[char])
                i += 1
                continue

            # ── Grade 2 group signs ──────────────────────────────────
            if char in GRADE2_GROUP_SIGNS:
                text = GRADE2_GROUP_SIGNS[char]
                if capitalize_next:
                    text = text.capitalize()
                    capitalize_next = False
                result.append(text)
                i += 1
                continue

            # ── Grade 1: letters + punctuation ───────────────────────
            if char in self._grade1:
                text = self._grade1[char]
                if capitalize_next:
                    text = text.upper()
                    capitalize_next = False
                # Space terminates number mode
                number_mode = False
                result.append(text)
                i += 1
                continue

            # ── Unknown character ────────────────────────────────────
            result.append("?")
            capitalize_next = False
            i += 1

        english = "".join(result)

        # ── Grade 2 short-form expansion ─────────────────────────────
        english = self._expand_short_forms(english)

        return english

    def full_pipeline(self, cells: list[dict]) -> dict:
        """
        Convenience: cells → {unicode_braille, english_text}.
        """
        unicode_braille = self.convert_to_unicode(cells)
        english_text = self.convert_to_english(unicode_braille)
        return {
            "unicode_braille": unicode_braille,
            "english_text": english_text,
        }

    # ── private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _expand_short_forms(text: str) -> str:
        """
        Replace Grade 2 short-form abbreviations with full words.
        Only replaces whole words to avoid mangling normal text.
        """
        words = text.split(" ")
        expanded = []
        for word in words:
            lower = word.lower()
            if lower in GRADE2_SHORT_FORMS:
                full = GRADE2_SHORT_FORMS[lower]
                # Preserve capitalisation of original
                if word[0].isupper():
                    full = full.capitalize()
                expanded.append(full)
            else:
                expanded.append(word)
        return " ".join(expanded)
