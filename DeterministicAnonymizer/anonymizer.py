import hashlib
from typing import Any, Dict

import numpy as np
import pandas as pd


class DeterministicAnonymizer:
    def __init__(self, key: str):
        """Initialize anonymizer with a secret key."""
        self.key = key.encode("utf-8")

    def _generate_seed(self, field_name: str) -> int:
        """Generate a deterministic seed for a field based on the key and field name."""
        h = hashlib.sha256(self.key + field_name.encode("utf-8"))
        return int(h.hexdigest(), 16) % (2**32)

    def _generate_numeric_noise(
        self,
        values: np.ndarray,
        field_name: str,
        amplitude: float,
        frequency: float,
    ) -> np.ndarray:
        """Generate deterministic sinusoidal noise for numeric values."""
        seed = self._generate_seed(field_name)
        indices = np.arange(len(values))

        # Generate deterministic phase based on the field's seed
        phase = np.random.RandomState(seed).rand() * 2 * np.pi

        # Generate sinusoidal noise
        noise = amplitude * np.sin(frequency * indices + phase)

        # Ensure the noise maintains the original dtype
        return noise.astype(values.dtype)

    def _text_transform(
        self,
        text: str,
        field_name: str,
        reverse: bool = False,
    ) -> str:
        """Transform text using deterministic character substitution.
        Only uses readable ASCII characters (letters, numbers, and basic punctuation).
        """
        if not isinstance(text, str):
            return text

        seed = self._generate_seed(field_name)
        result = []

        # Define the range of readable ASCII characters
        # 33-126 covers printable characters: ! through ~
        CHAR_RANGE = 94  # 126 - 33 + 1
        CHAR_START = 33  # '!' character

        for i, char in enumerate(text):
            # Generate deterministic hash for position
            h = hashlib.sha256(f"{seed}_{i}".encode())
            offset = int(h.hexdigest(), 16) % CHAR_RANGE

            # Get the ASCII value of the current character
            char_code = ord(char)

            if not reverse:
                # Forward transformation
                if CHAR_START <= char_code <= 126:
                    # If the character is in the readable range, transform within that range
                    new_char_code = (
                        (char_code - CHAR_START + offset) % CHAR_RANGE
                    ) + CHAR_START
                else:
                    # If the character is outside our range, map it into the readable range
                    new_char_code = (offset % CHAR_RANGE) + CHAR_START
            # Reverse transformation
            elif CHAR_START <= char_code <= 126:
                # Reverse the transformation within the readable range
                new_char_code = (
                    (char_code - CHAR_START - offset + CHAR_RANGE) % CHAR_RANGE
                ) + CHAR_START
            else:
                # If the character is outside our range, we can't properly reverse it
                # This should not happen if the text was encrypted with this same system
                new_char_code = char_code

            result.append(chr(new_char_code))

        return "".join(result)

    def anonymize(
        self,
        df: pd.DataFrame,
        config: Dict[str, Dict[str, Any]],
    ) -> pd.DataFrame:
        """Anonymize the DataFrame according to the configuration.

        config format:
        {
            'field_name': {
                'type': 'numeric'|'text',
                'amplitude': float,  # For numeric fields
                'frequency': float   # For numeric fields
            }
        }
        """
        result = df.copy()

        for field_name, field_config in config.items():
            if field_name not in df.columns:
                continue

            if field_config["type"] == "numeric":
                values = df[field_name].values
                noise = self._generate_numeric_noise(
                    values,
                    field_name,
                    field_config["amplitude"],
                    field_config["frequency"],
                )
                # Use numpy operations to maintain dtype
                result[field_name] = values + noise

            elif field_config["type"] == "text":
                # Vectorize the text transformation
                result[field_name] = df[field_name].apply(
                    lambda x: self._text_transform(x, field_name),
                )

        return result

    def deanonymize(
        self,
        df: pd.DataFrame,
        config: Dict[str, Dict[str, Any]],
    ) -> pd.DataFrame:
        """Reverse the anonymization process."""
        result = df.copy()

        for field_name, field_config in config.items():
            if field_name not in df.columns:
                continue

            if field_config["type"] == "numeric":
                values = df[field_name].values
                noise = self._generate_numeric_noise(
                    values,
                    field_name,
                    field_config["amplitude"],
                    field_config["frequency"],
                )
                # Use numpy operations to maintain dtype
                result[field_name] = values - noise

            elif field_config["type"] == "text":
                # Vectorize the text transformation
                result[field_name] = df[field_name].apply(
                    lambda x: self._text_transform(x, field_name, reverse=True),
                )

        return result
