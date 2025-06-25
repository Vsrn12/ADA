# Análisis de Red Social - Visualización de Grafos Por: Piero Adrian Delgado Chipana y Sebastian Adriano Castro Mamani

## 📋 Descripción

Esta aplicación de escritorio permite analizar y visualizar una red social masiva (hasta 10 millones de usuarios), mostrando sus conexiones en un mapa mundial interactivo. Destaca por la **implementación manual en Python de algoritmos clave** para el análisis de redes, como la detección de comunidades (Louvain), cálculo de caminos más cortos (BFS), y la generación de Árboles de Expansión Mínima (Kruskal). La visualización geográfica se realiza mediante **Folium**, ofreciendo una experiencia de mapa interactiva.

## 🚀 Características Principales

- **📁 Carga de Datos Masivos Eficiente**: Utiliza Polars para procesar eficientemente los archivos de ubicación y conexiones de usuarios.
- **🗺️ Visualización Global Interactiva con Folium**: Mapa mundial interactivo (zoom, paneo) con nodos distribuidos geográficamente y pop-ups informativos.
- **👥 Detección de Comunidades (Louvain Manual)**: Implementación manual del algoritmo de Louvain para identificar comunidades dentro de la red. Las comunidades se visualizan con colores distintos.
- **🛣️ Análisis de Caminos (BFS Manual)**: Cálculo manual del camino más corto entre nodos usando el algoritmo Breadth-First Search (BFS). El camino se resalta en el mapa.
- **🌳 Árbol de Expansión Mínima (Kruskal Manual)**: Implementación manual del algoritmo de Kruskal para encontrar el Árbol de Expansión Mínima (MST) del grafo de la red. El MST puede visualizarse en el mapa.
- **📊 Estadísticas Detalladas (Implementación Manual)**: Cálculo y visualización de métricas de red como número de nodos/aristas, densidad, componentes conectados, grado promedio y coeficiente de clustering, todas implementadas manualmente.
- **🛠️ Estructura de Grafo Personalizada**: Utiliza una clase `CustomGraph` propia para la representación y manipulación de los datos del grafo.
- **🎨 Interfaz Gráfica con Tkinter**: Aplicación de escritorio intuitiva construida con Tkinter.

## 📦 Instalación

1.  **Clonar o descargar el proyecto.**
2.  **Configurar Entorno Virtual (Recomendado):**
    ```bash
    python -m venv .venv
    # Activar el entorno:
    # Windows: .venv\Scripts\activate
    # macOS/Linux: source .venv/bin/activate
    ```
3.  **Instalar dependencias:**
    Asegúrate de estar en el directorio raíz del proyecto (el que contiene `README.md` y la carpeta `Ada Final LL`). Luego, instala las dependencias especificadas en el archivo `requirements.txt` que se encuentra dentro de `Ada Final LL/`:
    ```bash
    pip install -r "Ada Final LL/requirements.txt"
    ```
4.  **Colocar archivos de datos**:
    Los archivos `10_million_location.txt` y `10_million_user.txt` (o los nombres que hayas configurado en `Ada Final LL/config.py`) deben ubicarse en el **directorio raíz del proyecto**.
    ```
    TU_PROYECTO_RAIZ/
    ├── Ada Final LL/
    │   ├── main.py
    │   ├── requirements.txt
    │   └── ... (otros archivos .py)
    ├── 10_million_location.txt  <-- AQUÍ
    ├── 10_million_user.txt      <-- AQUÍ
    ├── README.md
    └── DETAILED_README.md
    ```
    Puedes ajustar las rutas exactas y nombres de archivo en `Ada Final LL/config.py`.

## 🎯 Uso

### Ejecutar la aplicación:
Desde el directorio `Ada Final LL/` (con el entorno virtual activado, si usas uno):
```bash
python main.py
```

### Flujo de trabajo:

1.  **📁 Cargar Datos**: Haz clic en "Cargar Datos" para procesar los archivos de ubicación y usuarios.
2.  **🗺️ Visualizar**: El mapa Folium mostrará los nodos en el navegador web. Puedes hacer zoom, paneo y clic en los nodos para ver información.
3.  **👥 Detectar Comunidades**: Usa "Detectar Comunidades" para ejecutar el algoritmo de Louvain. Los nodos se colorearán según su comunidad en el mapa.
4.  **🛣️ Analizar Caminos**: Ingresa los IDs de dos nodos y haz clic en "Camino Más Corto" para ver la ruta BFS resaltada.
5.  **🌳 Calcular MST**: Haz clic en "Calcular MST" para ejecutar el algoritmo de Kruskal y visualizar el árbol de expansión mínima.
6.  **📊 Ver Estadísticas**: "Generar Estadísticas" muestra métricas de la red en el panel lateral.

## 📁 Estructura del Proyecto

```
TU_PROYECTO_RAIZ/
├── Ada Final LL/
│   ├── main.py               # Punto de entrada principal.
│   ├── gui_app.py            # Lógica de la GUI (Tkinter) y visualización (Folium).
│   ├── graph_analyzer.py     # Orquestación del análisis del grafo.
│   ├── custom_graph.py       # Representación personalizada del grafo.
│   ├── algorithms.py         # Implementaciones manuales de algoritmos.
│   ├── loader.py             # Carga de datos con Polars.
│   ├── config.py             # Configuraciones.
│   ├── eda.py                # Script para Análisis Exploratorio (opcional).
│   ├── utils.py              # Utilidades (para EDA).
│   ├── requirements.txt      # Dependencias.
│   └── ...                   # Otros archivos generados (logs, etc.)
├── 10_million_location.txt   # Datos de ubicación (ejemplo).
├── 10_million_user.txt       # Datos de usuarios/conexiones (ejemplo).
├── README.md                 # Este archivo.
└── DETAILED_README.md        # Explicación técnica detallada.
```

## 🔧 Configuración

Edita `Ada Final LL/config.py` para ajustar:
- Nombres de los archivos de datos (`LOCATION_FILE`, `USER_FILE`).
- `SAMPLE_SIZE`: Número de usuarios a muestrear (`None` para el conjunto completo).
- `MAX_NODES_DISPLAY`: Límite de nodos a mostrar en el mapa Folium.

## ✨ Funcionalidades y Detalles Técnicos

Este proyecto destaca por la implementación manual de algoritmos clave de análisis de redes y su integración en una aplicación interactiva.

- **Estructura de Grafo Personalizada (`CustomGraph`)**: Base para todas las operaciones de grafos.
- **Análisis de Red Manual**: Cálculo de densidad, componentes, clustering, etc.
- **Algoritmos Implementados Manualmente**:
    - **Detección de Comunidades (Louvain)**
    - **Camino Más Corto (BFS)**
    - **Árbol de Expansión Mínima (Kruskal con Union-Find)**
- **Interfaz de Usuario**: Tkinter para la aplicación de escritorio, con mapas interactivos generados por Folium y mostrados en el navegador.
- **Optimización**: Carga de datos con Polars, muestreo para grandes datasets, y operaciones asíncronas en la GUI.

Para una **descripción exhaustiva** de cada módulo, las clases, funciones, los algoritmos implementados, el manejo de datos y más detalles técnicos, consulta el archivo:
➡️ **[`DETAILED_README.md`](DETAILED_README.md)**

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**: Lenguaje principal.
- **Tkinter**: Para la interfaz gráfica de usuario.
- **Folium**: Para la creación de mapas HTML interactivos.
- **Webbrowser**: Para mostrar los mapas Folium.
- **Polars**: Para la carga y manipulación eficiente de datos.
- **Numpy**: Para operaciones numéricas.
- **Pandas, Matplotlib, Seaborn**: Utilizados en el script `eda.py` opcional.
