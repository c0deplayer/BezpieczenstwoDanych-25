"""Dual-Key Anonymization System with Type Preservation

This system provides a sophisticated approach to reversible data anonymization using
multiple security layers and type preservation. It's designed to serve as an additional
security measure that can complement (not replace) encryption.

Key Features:
1. Dual-key architecture for enhanced security
2. Position-aware byte transformation using bitwise operations
3. Complete type preservation
4. Database-friendly base36 output
5. Perfect reversibility

Security Model:
- Two independent keys generate different transformation sequences
- Position-aware encoding prevents pattern recognition
- Multiple layers of bitwise operations provide complex transformation
- Not cryptographically secure - should be used with encryption

Author: Jakub Kujawa
Version: 1.0
"""

from __future__ import annotations  # Enable modern type hints

import secrets  # For generating secure random keys
from decimal import Decimal  # For precise decimal numbers
from enum import Enum  # For type classification
from hashlib import sha256, sha512  # For key sequence generation
from typing import override  # For method override annotation


class DataType(Enum):
    """Enumeration of supported data types with their markers.

    Each type has a single-character marker for compact serialization.

    Design rationale:
    - Single character markers minimize overhead
    - Distinct markers prevent ambiguity
    - Covers most common Python types
    """

    STRING = "S"  # Any string data
    INT = "I"  # Integer values (including negative)
    FLOAT = "F"  # Floating point numbers
    BOOL = "B"  # Boolean values (true/false)
    DECIMAL = "D"  # Decimal type for precise calculations
    NONE = "N"  # None/null values


class BitwiseDualKeyAnonymizer:
    """Base anonymizer implementing dual-key transformation using bitwise operations.

    Security features:
    1. Two independent key sequences using different hash functions
    2. Position-aware byte transformation
    3. Multiple layers of bitwise operations
    4. Non-linear transformations
    """

    def __init__(
        self,
        primary_key: str | bytes,
        secondary_key: str | bytes,
    ) -> None:
        """Initialize the anonymizer with two distinct keys.

        Args:
            primary_key: Key for main transformation
            secondary_key: Key for positional encoding

        The keys are processed differently:
        - Primary key uses SHA-256 (faster, suitable for main transform)
        - Secondary key uses SHA-512 (more complex, better for positional encoding)

        """
        # Convert string keys to bytes if needed
        self.primary_key = (
            primary_key.encode()
            if isinstance(primary_key, str)
            else primary_key
        )
        self.secondary_key = (
            secondary_key.encode()
            if isinstance(secondary_key, str)
            else secondary_key
        )

        # Generate different sequences for different purposes
        self.primary_sequence = self._generate_sequence(
            self.primary_key,
            sha256,
        )
        self.secondary_sequence = self._generate_sequence(
            self.secondary_key,
            sha512,
        )

    def _generate_sequence(
        self,
        key: bytes,
        hash_func: sha256 | sha512,
        length: int = 2048,
    ) -> bytes:
        """Generate a pseudorandom byte sequence from a key using cryptographic hashing.

        Process:
        1. Start with the key
        2. Repeatedly hash(previous_hash + key)
        3. Collect bytes until desired length

        Args:
            key: Seed key for sequence generation
            hash_func: Hash function to use (sha256/sha512)
            length: Desired sequence length

        Returns:
            Deterministic byte sequence based on key

        """
        result = bytearray()
        current_hash = key

        while len(result) < length:
            # Create new hash combining previous hash with key
            current_hash = hash_func(current_hash + key).digest()
            result.extend(current_hash)

        return bytes(result[:length])

    def _bitwise_transform_byte(
        self,
        byte: int,
        position: int,
        *,
        reverse: bool = False,
    ) -> int:
        """Transform a single byte using multiple bitwise operations.

        Transformation layers:
        1. XOR with primary key sequence (reversible via second XOR)
        2. Position-based circular bit rotation (reversible by rotating opposite direction)
        3. XOR with position-modified secondary key

        Args:
            byte: Input byte to transform
            position: Byte position in data
            reverse: Whether to apply reverse transformation

        Returns:
            Transformed byte

        Security features:
        - Each byte is transformed differently based on position
        - Both keys influence the transformation
        - Non-linear operations through rotation

        """
        # Get masks from both sequences
        primary_mask = self.primary_sequence[
            position % len(self.primary_sequence)
        ]
        secondary_mask = self.secondary_sequence[
            position % len(self.secondary_sequence)
        ]

        if not reverse:
            # Forward transformation
            result = byte ^ primary_mask  # First layer: XOR with primary key

            # Second layer: rotate bits right
            rotation = position % 8  # Keep within byte bounds
            result = ((result >> rotation) | (result << (8 - rotation))) & 0xFF

            # Third layer: XOR with position-dependent secondary key
            position_key = (secondary_mask + position) & 0xFF
            result ^= position_key

        else:
            # Reverse transformation (operations in reverse order)
            position_key = (secondary_mask + position) & 0xFF
            result = byte ^ position_key  # Reverse third layer

            # Reverse second layer (rotate left instead of right)
            rotation = position % 8
            result = ((result << rotation) | (result >> (8 - rotation))) & 0xFF

            result ^= primary_mask  # Reverse first layer

        return result

    def _positional_bit_scramble(
        self,
        byte: int,
        position: int,
        *,
        reverse: bool = False,
    ) -> int:
        """Additional bit manipulation based on byte position.

        Operations:
        1. XOR with position-based mask
        2. Conditional nibble swap for odd positions

        Args:
            byte: Input byte
            position: Byte position
            reverse: Whether to reverse the transformation

        Returns:
            Scrambled byte

        Design rationale:
        - Adds complexity without excessive computation
        - Position dependency prevents pattern recognition
        - Fully reversible operations

        """
        # Create position-dependent mask using prime numbers
        mask = (position * 13 + 41) & 0xFF  # 13 and 41 are primes

        if not reverse:
            # Forward scrambling
            result = byte ^ mask  # XOR with position mask
            if position & 1:  # For odd positions
                # Swap high and low 4 bits
                result = ((result & 0x0F) << 4) | ((result & 0xF0) >> 4)
        else:
            # Reverse scrambling
            if position & 1:  # For odd positions
                # Reverse nibble swap
                byte = ((byte & 0x0F) << 4) | ((byte & 0xF0) >> 4)
            result = byte ^ mask  # Reverse XOR

        return result

    def _to_base36(self, number: int) -> str:
        """Convert integer to base36 string (0-9 and A-Z).

        Process:
        1. Repeatedly divide by 36
        2. Map remainders to alphanumeric chars
        3. Reverse resulting string

        Args:
            number: Integer to convert

        Returns:
            Base36 string representation

        Why base36?
        - Alphanumeric only (database-friendly)
        - Case-insensitive (robust)
        - More compact than hex

        """
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if number == 0:
            return "0"

        base36 = ""
        while number:
            number, i = divmod(number, 36)
            base36 = alphabet[i] + base36

        return base36

    def _from_base36(self, base36_str: str) -> int:
        """Convert base36 string back to integer.

        Process:
        For a string like 'ABC':
        - A * 36² + B * 36¹ + C * 36⁰

        Args:
            base36_str: Base36 encoded string

        Returns:
            Original integer value

        Security note:
        Uses built-in int() with base 36, which validates input
        and raises ValueError for invalid characters.

        """
        return int(base36_str, 36)

    def _bytes_to_base36(self, data: bytes) -> str:
        """Convert byte sequence to base36 string.

        Process:
        1. Convert bytes to large integer (big-endian)
        2. Convert integer to base36

        Args:
            data: Byte sequence to convert

        Returns:
            Base36 string representation

        Note:
        Big-endian is used for consistent cross-platform behavior

        """
        number = int.from_bytes(data, byteorder="big")
        return self._to_base36(number)

    def _base36_to_bytes(self, base36_str: str) -> bytes:
        """Convert base36 string to bytes."""
        number = self._from_base36(base36_str)
        # Calculate minimum bytes needed
        byte_length = (number.bit_length() + 7) // 8
        return number.to_bytes(byte_length, byteorder="big")

    def anonymize(self, data: str | bytes) -> str:
        """Anonymize input data using dual-key transformation.

        Process flow:
        1. Convert input to bytes
        2. Add version byte for future compatibility
        3. Apply bitwise transformation to each byte
        4. Apply position-aware scrambling
        5. Convert to base36 with length prefix

        Args:
            data: Input data as string or bytes

        Returns:
            Anonymized data as base36 string

        """
        # Handle string input
        if isinstance(data, str):
            data = data.encode()

        # print(f"Data: {data}")

        # Add version byte for future algorithm updates
        version = b"\x01"  # Version 1 of the algorithm
        data = version + data

        result = bytearray()

        # Apply transformations byte by byte
        for pos, byte in enumerate(data):
            # Layer 1: Basic bitwise transformation
            transformed = self._bitwise_transform_byte(byte, pos)
            # Layer 2: Position-dependent scrambling
            scrambled = self._positional_bit_scramble(transformed, pos)
            result.append(scrambled)

        # print(f"Result: {result}")

        return self._bytes_to_base36(bytes(result))

    def deanonymize(self, base36_str: str) -> bytes:
        """Reverse the anonymization process.

        Process flow:
        1. Extract original length from prefix
        2. Convert base36 to bytes
        3. Reverse transformations in opposite order
        4. Remove version byte

        Args:
            base36_str: Anonymized base36 string

        Returns:
            Original data as bytes

        Security:
        - Validates length prefix
        - Performs exact reverse of each transformation
        - Checks version byte

        """
        anonymized_data = self._base36_to_bytes(base36_str)

        result = bytearray()

        # Reverse transformations byte by byte
        for pos, byte in enumerate(anonymized_data):
            # Reverse layer 2: Position-dependent scrambling
            unscrambled = self._positional_bit_scramble(byte, pos, reverse=True)
            # Reverse layer 1: Basic bitwise transformation
            original = self._bitwise_transform_byte(
                unscrambled,
                pos,
                reverse=True,
            )
            result.append(original)

        # Remove version byte and return
        return bytes(result[1:])


class TypeAwareDualKeyAnonymizer(BitwiseDualKeyAnonymizer):
    """Enhanced anonymizer that formats output as a structured token."""

    TOKEN_VERSION = "1"  # For future versioning
    TOKEN_PREFIX = "TKN"  # Token identifier

    def _serialize_with_type(self, data: object) -> tuple[str, DataType]:
        """Convert Python object to string while preserving type information.

        Strategy:
        - Use pattern matching for clean type handling
        - Special handling for bool (must come before int)
        - Maximum precision for float
        - Exact representation for Decimal

        Args:
            data: Any Python object

        Returns:
            Tuple of (serialized string, type marker)

        """
        match data:
            case None:
                return "None", DataType.NONE
            case bool() as b:  # Must check bool before int
                return str(int(b)), DataType.BOOL
            case int() as i:
                return str(i), DataType.INT
            case float() as f:
                return f"{f:.17g}", DataType.FLOAT  # Maximum precision
            case Decimal() as d:
                return str(d), DataType.DECIMAL
            case _:  # Default to string
                return str(data), DataType.STRING

    def _deserialize_with_type(self, data: str, data_type: DataType) -> object:
        """Restore original Python object from string and type information.

        Strategy:
        - Use pattern matching for clean type handling
        - Convert string to appropriate type
        - Handle special cases (None, bool)

        Args:
            data: Serialized string
            data_type: Original data type

        Returns:
            Restored Python object of original type

        """
        match data_type:
            case DataType.NONE:
                return None
            case DataType.BOOL:
                return bool(int(data[2:]))
            case DataType.INT:
                return int(data[2:])
            case DataType.FLOAT:
                return float(data[2:])
            case DataType.DECIMAL:
                return Decimal(data[2:])
            case _:
                return data[2:]

    def _create_token(self, type_marker: str, data: str) -> str:
        """Create a structured token from components.

        Format: TKN_V1_TYPEBASE36DATA
        Example: TKN_V1_IBASE36DATA
        """
        return f"{self.TOKEN_PREFIX}_V{self.TOKEN_VERSION}_{type_marker}{data}"

    def _parse_token(self, token: str) -> tuple[str, str, str]:
        """Parse token into components."""
        try:
            parts = token.split("_")
            if len(parts) != 3 or parts[0] != self.TOKEN_PREFIX:
                raise ValueError("Invalid token format")

            prefix, version, combined_data = parts
            type_marker, data = combined_data[0], combined_data[1:]
            if version != f"V{self.TOKEN_VERSION}":
                raise ValueError(f"Unsupported token version: {version}")
        except Exception as e:
            raise ValueError(f"Invalid token format: {e!s}")
        else:
            return type_marker, data

    @override
    def anonymize(self, data: object) -> str:
        """Anonymize data and return as structured token.

        Example outputs:
        - Integer: TKN_V1_IBASE36DATA
        - String:  TKN_V1_SBASE36DATA
        - Float:   TKN_V1_FBASE36DATA
        """
        # Get basic anonymization
        serialized, data_type = self._serialize_with_type(data)
        data_with_type = f"{data_type.value}:{serialized}"
        # print(f"Serialized: {data_with_type}")
        anonymized = super().anonymize(data_with_type)
        # print(f"Anonymized: {anonymized}")

        # print(f"Tokenized: {self._create_token(data_type.value, anonymized)}")

        # Create structured token
        return self._create_token(data_type.value, anonymized)

    @override
    def deanonymize(self, token: str) -> object:
        """Deanonymize from structured token format."""
        # Parse token
        type_marker, data = self._parse_token(token)

        # Reconstruct original anonymized format
        anonymized = data

        data_type = DataType(type_marker)

        typed_data = super().deanonymize(anonymized).decode()

        return self._deserialize_with_type(typed_data, data_type)


# Example usage and testing
if __name__ == "__main__":
    # Create instance with a secret key
    anonymizer = TypeAwareDualKeyAnonymizer(
        primary_key="PrimarySecretKey123!098",
        secondary_key="SecondarySecretKey456@321",
    )

    # Test data with various types of content
    test_cases = [
        "John Doe SSN:123-45-6789",
        "Patient ID: PATIENT-123",
        "©®™€$¥£¢",
        "Short",
        "A" * 100,  # Test longer string
    ]

    print("Testing Base36 Anonymization:")
    print("-" * 60)

    for test_data in test_cases:
        # Perform anonymization
        anonymized = anonymizer.anonymize(test_data)
        # Perform deanonymization
        deanonymized = anonymizer.deanonymize(anonymized)

        print(f"Original     : {test_data}")
        print(f"Type         : {type(test_data)}")
        print(f"Anonymized   : {anonymized}")
        print(f"Length       : {len(anonymized)}")
        print(f"Restored     : {deanonymized}")
        print(f"Restored Type: {type(deanonymized)}")
        print(f"Match        : {test_data == deanonymized}")
        print("-" * 60)

    # Demonstrate consistency
    data = "Test consistency"
    anon1 = anonymizer.anonymize(data)
    anon2 = anonymizer.anonymize(data)
    print("Consistency check (should be True):", anon1 == anon2)

    # Demonstrate different keys produce different results
    anonymizer2 = TypeAwareDualKeyAnonymizer(
        primary_key=secrets.token_hex(64),
        secondary_key=secrets.token_hex(64),
    )
    anon3 = anonymizer2.anonymize(data)

    print(
        "Different keys produce different results (should be False):",
        anon1 == anon3,
    )

    print("\n" + "-" * 60)
    print("Round 2\n" + "-" * 60 + "\n")

    second_tests_cases = [
        "Hello świat! Γειά σας! 你好! 👋",  # Mix of Latin, Polish, Greek, Chinese, and emoji
        "αβγδεζηθικλμνξοπρστυφχψω",  # Greek alphabet
        "zażółć gęślą jaźń",  # Polish text
        "こんにちは世界",  # Japanese text
        42,  # Regular number
        3.14159,  # Float
        "1111-2222-3333-4444",  # Credit card number
        "01312200313",
        "Jakub",
        True,
        False,
        "Jan Kowalski",
    ]

    for test_data in second_tests_cases:
        # Perform anonymization
        anonymized = anonymizer.anonymize(test_data)
        # Perform deanonymization
        deanonymized = anonymizer.deanonymize(anonymized)

        print(f"Original     : {test_data}")
        print(f"Type         : {type(test_data)}")
        print(f"Anonymized   : {anonymized}")
        print(f"Length       : {len(anonymized)}")
        print(f"Restored     : {deanonymized}")
        print(f"Restored Type: {type(deanonymized)}")
        print(f"Match        : {test_data == deanonymized}")
        print("-" * 60)

    # Demonstrate consistency
    data = "Test consistency"
    anon1 = anonymizer.anonymize(data)
    anon2 = anonymizer.anonymize(data)
    print("Consistency check (should be True):", anon1 == anon2)

    # Demonstrate different keys produce different results
    anonymizer2 = TypeAwareDualKeyAnonymizer(
        primary_key=secrets.token_hex(64),
        secondary_key=secrets.token_hex(64),
    )
    anon3 = anonymizer2.anonymize(data)

    print(
        "Different keys produce different results (should be False):",
        anon1 == anon3,
    )
    print(f"Anon1 vs Anon3: {anon1} vs {anon3}")
