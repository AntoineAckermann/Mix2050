import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("eco2mix-national-cons-def.csv", sep=";")
df.dropna(axis="index", inplace=True)
df.reset_index(inplace=True)
df.drop(["Périmètre", "Nature"], axis=1, inplace=True)
df.rename(columns={"Taux de CO2 (g/kWh)": "CO2"}, inplace=True)
df.rename(lambda x: x.replace(" (MW)", ""), axis="columns", inplace=True)
df["Date et Heure"] = pd.to_datetime(df["Date et Heure"], format="%Y-%m-%dT%H:%M:%S")
df["Date et Heure"] = df["Date et Heure"].apply(lambda x: x.replace(tzinfo=None))
df.set_index("Date et Heure", inplace=True)
df.drop(["index"], axis="columns", inplace=True)

parc = pd.read_csv("parc-prod-par-filiere.csv", sep="\t")
parc.set_index("Annee", inplace=True)
parc.rename(lambda x: x.replace(" (MW)", ""), axis="columns", inplace=True)

df["Solaire normalisé"] = df["Solaire"]/parc.loc[2019, "Parc solaire"]
df["Eolien normalisé"] = df["Eolien"]/parc.loc[2019, "Parc eolien"]

df.to_pickle("dataRTE.pkl")
parc.to_pickle("parcRTE.pkl")


df.loc["2019", ["Solaire normalisé", "Eolien normalisé"]].resample("D").mean().plot()
plt.show()

