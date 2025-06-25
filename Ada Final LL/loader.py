import polars as pl
import os
import logging

def load_location_data(filepath: str):
    try:
        logging.info(f"Cargando archivo de ubicación: {filepath}")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo {filepath} no existe.")

        # Read as strings first to allow adding row index before casting
        # Assuming the row number acts as the ID (0-indexed)
        df = pl.read_csv(filepath, has_header=False, new_columns=["lat_str", "long_str"])
        df = df.with_row_index("id", offset=0) # Add 0-indexed ID as first column
        df = df.with_columns([
            pl.col("lat_str").cast(pl.Float64).alias("lat"),
            pl.col("long_str").cast(pl.Float64).alias("long"),
        ]).drop("lat_str", "long_str")
        logging.info(f"Archivo de ubicación cargado: {df.height} registros")
        return df
    except Exception as e:
        logging.error(f"Error al cargar datos de ubicación: {e}")
        return None

def load_user_data(filepath: str):
    try:
        logging.info(f"Cargando archivo de usuarios: {filepath}")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo {filepath} no existe.")

        with open(filepath, "r") as f:
            lines = (line.strip() for line in f)
            # The 'adj_list' column will hold the original string, e.g., "0 1 2"
            df = pl.DataFrame({"adj_list": list(lines)})

        logging.info(f"Archivo de usuarios cargado: {df.height} registros")
        return df
    except Exception as e:
        logging.error(f"Error al cargar datos de usuario: {e}")
        return None