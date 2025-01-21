import pandas as pd
# dodać wzrost i płeć
# df = pd.read_csv("/home/wojciech/Dokumenty/Wojtek/Projekty/bezp/people_data_4.csv", header=0)

# print(df.head(), "\nprzerwa\n", len(df))



# imie = df["name"][0]
# print(imie.head())
'''
df[["name", "last name"]] = df["name"].str.split(" ", n=1, expand=True)
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
'''

def anonimizacja(dane, klucz):
    klucz[0] = klucz[0] % len(dane)
    klucz[1] = klucz[1] % len(dane)
    # podział danych
    dane[["name", "last name"]] = dane["name"].str.split(" ", n=1, expand=True)
    dane["ssn_1"] = dane["ssn"].str[:5]
    dane["ssn_2"] = dane["ssn"].str[5:]

    # imię
    dane["name"] = pd.concat([
        dane["name"].iloc[klucz[0]:], 
        dane["name"].iloc[:klucz[0]]
    ]).reset_index(drop=True)

    # nazwisko
    dane["last name"] = pd.concat([
        dane["last name"].iloc[-klucz[1]:], 
        dane["last name"].iloc[:-klucz[1]]
    ]).reset_index(drop=True)

    # ssn_1
    dane["ssn_1"] = pd.concat([
        dane["ssn_1"].iloc[klucz[0]:], 
        dane["ssn_1"].iloc[:klucz[0]]
    ]).reset_index(drop=True)

    # ssn_2
    dane["ssn_2"] = pd.concat([
        dane["ssn_2"].iloc[-klucz[1]:], 
        dane["ssn_2"].iloc[:-klucz[1]]
    ]).reset_index(drop=True)

    dane["ssn"] = dane["ssn_1"] + dane["ssn_2"]
    dane.drop(["ssn_1", "ssn_2"], axis=1, inplace=True)

    dane["name"] = dane["name"] + " " + dane["last name"]
    dane.drop(columns=["last name"], inplace=True)
    
    return dane

def deanonimizacja(dane, klucz):
    klucz[0] = klucz[0] % len(dane)
    klucz[1] = klucz[1] % len(dane)
    # podział danych
    dane[["name", "last name"]] = dane["name"].str.split(" ", n=1, expand=True)
    dane["ssn_1"] = dane["ssn"].str[:5]
    dane["ssn_2"] = dane["ssn"].str[5:]

    # imię
    dane["name"] = pd.concat([
        dane["name"].iloc[-klucz[0]:], 
        dane["name"].iloc[:-klucz[0]]
    ]).reset_index(drop=True)

    # nazwisko
    dane["last name"] = pd.concat([
        dane["last name"].iloc[klucz[1]:], 
        dane["last name"].iloc[:klucz[1]]
    ]).reset_index(drop=True)

    # ssn_1
    dane["ssn_1"] = pd.concat([
        dane["ssn_1"].iloc[-klucz[0]:], 
        dane["ssn_1"].iloc[:-klucz[0]]
    ]).reset_index(drop=True)

    # ssn_2
    dane["ssn_2"] = pd.concat([
        dane["ssn_2"].iloc[klucz[1]:], 
        dane["ssn_2"].iloc[:klucz[1]]
    ]).reset_index(drop=True)

    dane["ssn"] = dane["ssn_1"] + dane["ssn_2"]
    dane.drop(["ssn_1", "ssn_2"], axis=1, inplace=True)

    dane["name"] = dane["name"] + " " + dane["last name"]
    dane.drop(columns=["last name"], inplace=True)
    
    return dane

klucz = [1, 3]

from faker import Faker
import random
import json

fake = Faker()

print(fake.country())
print(fake.name())
print(random.randint(1, 100)) # wiek
print(fake.ssn())
print(fake.company())

def generate_fake_data():
    return {
        "country": fake.country(),
        "name": fake.name(),
        "age": random.randint(1, 100),
        "ssn": fake.ssn(),
        "height": random.randint(140, 210),
        "gender": random.choice(["M", "F"]),
        "company": fake.company()
    }

def generowanie_wielu(num_records=100):
    return [generate_fake_data() for _ in range(num_records)]

people_data = generowanie_wielu(10)
with open("people_data.json", "w") as file:
    json.dump(people_data, file, indent=4, default=str)

df = pd.read_json("people_data.json")

anon = anonimizacja(df.copy(), klucz) # to było dobrze ale nie zrobiłem .copy()
print(df.head(), "\nprzerwa\n")
print(anonimizacja(df, klucz).head(), "\nprzerwa\n")
print(deanonimizacja(anon, klucz).head())
