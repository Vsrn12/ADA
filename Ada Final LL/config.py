# config.py

LOCATION_FILE = "10_million_location.txt"
USER_FILE = "10_million_user.txt"

# Configuración de la aplicación
APP_TITLE = "Análisis de Red Social - Visualización de Grafos"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# --- CONFIGURACIÓN MODIFICADA PARA GRAFO COMPLETO ---

# Configuración de visualización
# ADVERTENCIA: Visualizar demasiados nodos puede ser extremadamente lento o bloquear la aplicación.
MAX_NODES_DISPLAY = None 

# Muestreo de datos inicial. 
# Esta es la variable MÁS IMPORTANTE. Cámbiala a 'None' para leer y procesar todos los datos.
SAMPLE_SIZE = 10000

# Límite de nodos para el subgrafo del camino más corto.
# Al ponerlo en 'None', eliminas el límite para esta función específica,
MAX_PATH_NODES = None # Antes estaba en 1000