"""Column-based data anonymization module.

This module implements data anonymization by splitting and shifting columns
independently using a two-element key. Specifically designed for handling
personal data with special focus on names and SSN numbers.
"""

import json
import random
from typing import TypedDict

import pandas as pd
from faker import Faker


class PersonData(TypedDict):
    """Structure representing a person's data record."""

    country: str
    name: str
    age: int
    ssn: str
    height: int
    gender: str
    company: str


def anonimizacja(dane: pd.DataFrame, klucz: list[int]) -> pd.DataFrame:
    """Anonymize data by splitting and shifting name and SSN columns.

    Args:
        dane: Input DataFrame containing at least 'name' and 'ssn' columns
        klucz: Two-element list containing shift values for different parts

    Returns:
        DataFrame with anonymized name and SSN values

    """
    klucz[0] = klucz[0] % len(dane)
    klucz[1] = klucz[1] % len(dane)
    # podział danych
    dane[["name", "last name"]] = dane["name"].str.split(" ", n=1, expand=True)
    dane["ssn_1"] = dane["ssn"].str[:5]
    dane["ssn_2"] = dane["ssn"].str[5:]

    # imię
    dane["name"] = pd.concat(
        [
            dane["name"].iloc[klucz[0] :],
            dane["name"].iloc[: klucz[0]],
        ],
    ).reset_index(drop=True)

    # nazwisko
    dane["last name"] = pd.concat(
        [
            dane["last name"].iloc[-klucz[1] :],
            dane["last name"].iloc[: -klucz[1]],
        ],
    ).reset_index(drop=True)

    # ssn_1
    dane["ssn_1"] = pd.concat(
        [
            dane["ssn_1"].iloc[klucz[0] :],
            dane["ssn_1"].iloc[: klucz[0]],
        ],
    ).reset_index(drop=True)

    # ssn_2
    dane["ssn_2"] = pd.concat(
        [
            dane["ssn_2"].iloc[-klucz[1] :],
            dane["ssn_2"].iloc[: -klucz[1]],
        ],
    ).reset_index(drop=True)

    dane["ssn"] = dane["ssn_1"] + dane["ssn_2"]
    dane.drop(["ssn_1", "ssn_2"], axis=1, inplace=True)

    dane["name"] = dane["name"] + " " + dane["last name"]
    dane.drop(columns=["last name"], inplace=True)

    return dane


def deanonimizacja(dane: pd.DataFrame, klucz: list[int]) -> pd.DataFrame:
    """Restore original data by reversing the anonymization process.

    Args:
        dane: Anonymized DataFrame
        klucz: Same two-element list used for anonymization

    Returns:
        DataFrame with restored original values

    """
    klucz[0] = klucz[0] % len(dane)
    klucz[1] = klucz[1] % len(dane)
    # podział danych
    dane[["name", "last name"]] = dane["name"].str.split(" ", n=1, expand=True)
    dane["ssn_1"] = dane["ssn"].str[:5]
    dane["ssn_2"] = dane["ssn"].str[5:]

    # imię
    dane["name"] = pd.concat(
        [
            dane["name"].iloc[-klucz[0] :],
            dane["name"].iloc[: -klucz[0]],
        ],
    ).reset_index(drop=True)

    # nazwisko
    dane["last name"] = pd.concat(
        [
            dane["last name"].iloc[klucz[1] :],
            dane["last name"].iloc[: klucz[1]],
        ],
    ).reset_index(drop=True)

    # ssn_1
    dane["ssn_1"] = pd.concat(
        [
            dane["ssn_1"].iloc[-klucz[0] :],
            dane["ssn_1"].iloc[: -klucz[0]],
        ],
    ).reset_index(drop=True)

    # ssn_2
    dane["ssn_2"] = pd.concat(
        [
            dane["ssn_2"].iloc[klucz[1] :],
            dane["ssn_2"].iloc[: klucz[1]],
        ],
    ).reset_index(drop=True)

    dane["ssn"] = dane["ssn_1"] + dane["ssn_2"]
    dane.drop(["ssn_1", "ssn_2"], axis=1, inplace=True)

    dane["name"] = dane["name"] + " " + dane["last name"]
    dane.drop(columns=["last name"], inplace=True)

    return dane


def generate_fake_data() -> PersonData:
    """Generate a single record of fake personal data.

    Returns:
        Dictionary containing randomly generated person information

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


if __name__ == "__main__":
    klucz: list[int] = [1, 3]
    fake = Faker()

    people_data: list[PersonData] = generowanie_wielu(10)
    with open("people_data.json", "w") as file:
        json.dump(people_data, file, indent=4, default=str)

    df: pd.DataFrame = pd.read_json("people_data.json")
    anon: pd.DataFrame = anonimizacja(df.copy(), klucz)

    print(df.head(), "\nprzerwa\n")
    print(anonimizacja(df, klucz).head(), "\nprzerwa\n")
    print(deanonimizacja(anon, klucz).head())
