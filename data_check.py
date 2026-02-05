import streamlit as st
import pandas as pd
import plotly.express as px


#Datensatz laden
file_path = "ecommerce_sales.csv"
df = pd.read_csv(file_path)

#Die Struktur anzeigen lassen
print("-------- DATENSTRUKTUR---------")
print(df.info())

print("\n------- STATISCHE KENNZAHLEN ----------")
print(df.describe())

print("\n ------ DIE ERSTEN 5 ZEILEN  ------")
print(df.head())

print("\n------ SPALTENNAMEN ------")
print(df.columns.tolist())