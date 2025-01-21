import numpy as np
import pandas as pd
import json
import random

from faker import Faker

# dodać wzrost i płeć
# df = pd.read_csv(
#     "/home/wojciech/Dokumenty/Wojtek/Projekty/bezp/people_data_4.csv",
#     header=0,
# )

# print(df.head(), "\nprzerwa\n", len(df))


# imie = df["name"][0]
# print(imie.head())
"""df[["name", "last name"]] = df["name"].str.split(" ", n=1, expand=True)
df["ssn_1"] = df["ssn"].str[:5]
df["ssn_2"] = df["ssn"].str[5:]

print(df.head())

shift = 1

# iloc określa pozycję rekordu
df["name"] = pd.concat([
    df["name"].iloc[-shift:],
    df["name"].iloc[:-shift]
]).reset_index(drop=True)

print("przerwa\n", df.head())

shift = -2

df["name"] = pd.concat([
    df["name"].iloc[-shift:],
    df["name"].iloc[:-shift]
]).reset_index(drop=True)

print("przerwa\n", df.head())
"""


def anonimizacja(dane, klucz):
    n = len(dane)
    if n == 0:
        return dane
    shift_a = klucz[0] % n
    shift_b = klucz[1] % n

    result = dane.copy()
    for i, col in enumerate(dane.columns):
        values = dane[col].values  # Get numpy array
        if i % 2 == 0:
            # Use numpy roll for efficient shifting
            result[col] = np.roll(values, -shift_a)
        else:
            result[col] = np.roll(values, shift_b)
    return result


def deanonimizacja(dane, klucz):
    n = len(dane)
    if n == 0:
        return dane
    shift_a = klucz[0] % n
    shift_b = klucz[1] % n

    result = dane.copy()
    for i, col in enumerate(dane.columns):
        values = dane[col].values
        if i % 2 == 0:
            result[col] = np.roll(values, shift_a)
        else:
            result[col] = np.roll(values, -shift_b)
    return result


klucz = [3, 13]


fake = Faker()


def generate_fake_data():
    return {
        "country": fake.country(),
        "name": fake.name(),
        "age": random.randint(1, 100),
        "ssn": fake.ssn(),
        "height": random.randint(140, 210),
        "gender": random.choice(["M", "F"]),
        "company": fake.company(),
    }


def generowanie_wielu(num_records=100):
    return [generate_fake_data() for _ in range(num_records)]


people_data = generowanie_wielu(1000)
with open("people_data.json", "w") as file:
    json.dump(people_data, file, indent=4, default=str)

df = pd.read_json("people_data.json")


# df = pd.read_csv(
#     "/home/wojciech/Dokumenty/Wojtek/Projekty/bezp/people_data_4.csv",
#     header=0,
# )

anon = anonimizacja(df.copy(), klucz)  # to było dobrze ale nie zrobiłem .copy()
print(df.head(10), "\n\n-----------------------------\n")
print(anonimizacja(df, klucz).head(10), "\n\n-----------------------------\n")
print(deanonimizacja(anon, klucz).head(10))
