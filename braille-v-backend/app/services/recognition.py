"""
Braille-V Character Recognition Service
CNN-based classifier with dot-pattern fallback.
"""

import logging
from pathlib import Path

import cv2
import numpy as np

from app.utils.config import settings
from app.utils.grade2_mapping import GRADE1_MAP, dots_to_unicode

logger = logging.getLogger(__name__)


class BrailleRecognizer:
    """Recognise individual Braille characters from cell images or dot patterns."""

    def __init__(self, model_path: Path | None = None):
        self._model = None
        self._model_path = model_path or settings.CNN_MODEL_PATH
        self._char_map = self._create_char_map()
        self._load_model()

    # ── public API ───────────────────────────────────────────────────────

    def recognize_cell(self, cell_image: np.ndarray) -> str:
        """
        Recognise a single Braille cell from its image crop.

        Parameters
        ----------
        cell_image : np.ndarray
            Grayscale image of one Braille cell.

        Returns
        -------
        str
            The recognised character.
        """
        if self._model is not None:
            return self._cnn_predict(cell_image)

        # Fallback: simple dot-pattern lookup (no CNN needed)
        return "?"

    def recognize_from_dots(self, dot_positions: list[int]) -> str:
        """
        Recognise a Braille character directly from its dot positions.
        Uses the Grade 1 mapping table — no CNN required.

        Parameters
        ----------
        dot_positions : list[int]
            Raised dot numbers, e.g. [1, 2, 4] → 'f'.

        Returns
        -------
        str
            The recognised character.
        """
        unicode_char = dots_to_unicode(dot_positions)
        return GRADE1_MAP.get(unicode_char, "?")

    # ── private helpers ──────────────────────────────────────────────────

    def _load_model(self) -> None:
        if not self._model_path.exists():
            logger.warning(
                "CNN weights not found at %s – using dot-pattern fallback",
                self._model_path,
            )
            return

        try:
            import tensorflow as tf

            self._model = tf.keras.models.load_model(str(self._model_path))
            logger.info("CNN classifier loaded from %s", self._model_path)
        except Exception as exc:
            logger.warning("Failed to load CNN model: %s", exc)
            self._model = None

    def _cnn_predict(self, cell_image: np.ndarray) -> str:
        """Run CNN inference on a 48×48 grayscale cell image."""
        # Resize to expected input
        cell = cv2.resize(cell_image, (48, 48))

        # Ensure grayscale
        if len(cell.shape) == 3:
            cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)

        # Normalise to [0, 1] and reshape for the model
        cell = cell.astype("float32") / 255.0
        cell = np.expand_dims(cell, axis=0)   # batch dim
        cell = np.expand_dims(cell, axis=-1)  # channel dim

        prediction = self._model.predict(cell, verbose=0)
        class_index = int(np.argmax(prediction[0]))
        confidence = float(prediction[0][class_index])

        char = self._char_map.get(class_index, "?")
        logger.debug(
            "CNN prediction: class=%d char=%s confidence=%.3f",
            class_index,
            char,
            confidence,
        )
        return char

    @staticmethod
    def _create_char_map() -> dict[int, str]:
        """Map CNN class indices to characters.

        Layout: A-Z (0-25), 0-9 (26-35), punctuation (36-63).
        """
        chars = list("abcdefghijklmnopqrstuvwxyz")          # 0-25
        chars += list("0123456789")                          # 26-35
        chars += list(",.!?;:'\"-()&@#$/\\{}[]+=<>~`^|_")   # 36-63
        # Pad to 64 if needed
        while len(chars) < 64:
            chars.append("?")
        return {i: c for i, c in enumerate(chars[:64])}
