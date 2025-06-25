import matplotlib.pyplot as plt
import seaborn as sns
import polars as pl
import logging
import pandas as pd
from utils import detect_outliers_iqr

sns.set(style="whitegrid")

def run_location_eda(df: pl.DataFrame):
    logging.info("EDA de ubicación iniciado")

    # Estadísticas
    print(df.describe())

    # Visualización
    pd_df = df.to_pandas()

    plt.figure(figsize=(12, 5))
    sns.histplot(pd_df["lat"], kde=True, bins=100)
    plt.title("Distribución de latitudes")
    plt.xlabel("Latitud")
    plt.savefig("lat_hist.png")
    plt.close()

    plt.figure(figsize=(12, 5))
    sns.histplot(pd_df["long"], kde=True, bins=100, color="orange")
    plt.title("Distribución de longitudes")
    plt.xlabel("Longitud")
    plt.savefig("long_hist.png")
    plt.close()

    # Detección de outliers
    out_lat = detect_outliers_iqr(pd_df["lat"])
    out_long = detect_outliers_iqr(pd_df["long"])
    logging.info(f"Outliers latitud: {len(out_lat)}, Outliers longitud: {len(out_long)}")

def run_user_eda(df: pl.DataFrame):
    logging.info("EDA de usuarios iniciado")

    # Convertir a pandas para análisis más flexible
    pd_df = df.to_pandas()

    # Cantidad de vecinos por usuario
    pd_df["num_neighbors"] = pd_df["adj_list"].apply(lambda x: len(x.split()) if x else 0)

    print(pd_df["num_neighbors"].describe())

    # Visualización
    plt.figure(figsize=(12, 5))
    sns.histplot(pd_df["num_neighbors"], bins=100, kde=True)
    plt.title("Distribución del número de vecinos por usuario")
    plt.xlabel("Cantidad de vecinos")
    plt.savefig("user_neighbors_hist.png")
    plt.close()

    # Detección de outliers
    out_neighbors = detect_outliers_iqr(pd_df["num_neighbors"])
    logging.info(f"Outliers en vecinos: {len(out_neighbors)}")
