"""Shuffling-based anonymization module.

This module implements data anonymization through column shuffling using a key-based approach.
It provides functionality to generate fake data and perform reversible anonymization.
"""

import json
import random
from typing import TypedDict

import numpy as np
import pandas as pd
from faker import Faker


class PersonData(TypedDict):
    """Structure representing a person's data."""

    country: str
    name: str
    age: int
    ssn: str
    height: int
    gender: str
    company: str


def anonimizacja(dane: pd.DataFrame, klucz: list[int]) -> pd.DataFrame:
    """Anonymize data by shuffling columns based on a key.

    Args:
        dane: Input DataFrame to anonymize
        klucz: Two-element list containing shift values for even/odd columns

    Returns:
        Anonymized DataFrame with shuffled columns

    """
    n = len(dane)
    if n == 0:
        return dane
    shift_a = klucz[0] % n
    shift_b = klucz[1] % n

    result = dane.copy()
    for i, col in enumerate(dane.columns):
        values = dane[col].to_numpy()
        if i % 2 == 0:
            # Use numpy roll for efficient shifting
            result[col] = np.roll(values, -shift_a)
        else:
            result[col] = np.roll(values, shift_b)
    return result


def deanonimizacja(dane: pd.DataFrame, klucz: list[int]) -> pd.DataFrame:
    """Deanonymize previously anonymized data using the same key.

    Args:
        dane: Anonymized DataFrame
        klucz: Two-element list containing shift values for even/odd columns

    Returns:
        Original DataFrame with restored column values

    """
    n = len(dane)
    if n == 0:
        return dane
    shift_a = klucz[0] % n
    shift_b = klucz[1] % n

    result = dane.copy()
    for i, col in enumerate(dane.columns):
        values = dane[col].to_numpy()
        if i % 2 == 0:
            result[col] = np.roll(values, shift_a)
        else:
            result[col] = np.roll(values, -shift_b)
    return result


def generate_fake_data() -> PersonData:
    """Generate fake person data using Faker.

    Returns:
        Dictionary containing randomly generated person data

    """
    fake = Faker()
    return {
        "country": fake.country(),
        "name": fake.name(),
        "age": random.randint(1, 100),
        "ssn": fake.ssn(),
        "height": random.randint(140, 210),
        "gender": random.choice(["M", "F"]),
        "company": fake.company(),
    }


def generowanie_wielu(num_records: int = 100) -> list[PersonData]:
    """Generate multiple fake person records.

    Args:
        num_records: Number of records to generate

    Returns:
        List of randomly generated person data dictionaries

    """
    return [generate_fake_data() for _ in range(num_records)]


# Test code
if __name__ == "__main__":
    klucz: list[int] = [3, 13]
    fake = Faker()

    people_data: list[PersonData] = generowanie_wielu(1000)
    with open("people_data.json", "w") as file:
        json.dump(people_data, file, indent=4, default=str)

    df = pd.read_json("people_data.json")
    anon = anonimizacja(df.copy(), klucz)
    print(df.head(10), "\n\n-----------------------------\n")
    print(
        anonimizacja(df, klucz).head(10),
        "\n\n-----------------------------\n",
    )
    print(deanonimizacja(anon, klucz).head(10))
