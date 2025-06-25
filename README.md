# Análisis de Red Social - Visualización de Grafos

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
    # Windows: .venv\\Scripts\\activate
    # macOS/Linux: source .venv/bin/activate
    ```
3.  **Instalar dependencias:**
    Asegúrate de estar en el directorio `Ada Final LL/python_app/`.
    ```bash
    pip install -r requirements.txt
    ```
4.  **Colocar archivos de datos**:
    Los archivos `10_million_location.txt` y `10_million_user.txt` deben ubicarse en el directorio **padre** de `Ada Final LL/python_app/`. Por ejemplo:
    ```
    TU_PROYECTO_RAIZ/
    ├── Ada Final LL/
    │   └── python_app/
    │       ├── main.py
    │       └── ... (otros archivos .py)
    ├── 10_million_location.txt  <-- AQUÍ
    └── 10_million_user.txt      <-- AQUÍ
    ```
    Puedes ajustar las rutas en `Ada Final LL/python_app/config.py` si es necesario.

## 🎯 Uso

### Ejecutar la aplicación:
Desde el directorio `Ada Final LL/python_app/` (con el entorno virtual activado):
```bash
python main.py
```

### Flujo de trabajo:

1.  **📁 Cargar Datos**: Haz clic en "Cargar Datos" para procesar los archivos de ubicación y usuarios.
2.  **🗺️ Visualizar**: El mapa Folium mostrará automáticamente los nodos distribuidos globalmente. Puedes hacer zoom, paneo y clic en los nodos para ver información.
3.  **👥 Detectar Comunidades**: Usa "Detectar Comunidades" para ejecutar el algoritmo de Louvain manual. Los nodos se colorearán según su comunidad.
4.  **🛣️ Analizar Caminos**: Ingresa los IDs de dos nodos (inicio y fin) y haz clic en "Camino Más Corto" para ver la ruta BFS resaltada.
5.  **🌳 Calcular MST**: Haz clic en "Calcular MST" para ejecutar el algoritmo de Kruskal manual y visualizar el árbol de expansión mínima en el mapa.
6.  **📊 Ver Estadísticas**: Haz clic en "Generar Estadísticas" para ver métricas detalladas de la red en el panel lateral.

## 📁 Estructura del Proyecto

```
Ada Final LL/python_app/
├── main.py               # Punto de entrada principal de la aplicación.
├── gui_app.py            # Lógica de la interfaz gráfica de usuario (Tkinter + Folium).
├── graph_analyzer.py     # Clase que orquesta el análisis del grafo.
├── custom_graph.py       # Clase para la representación personalizada del grafo.
├── algorithms.py         # Implementaciones manuales de algoritmos de grafos.
├── loader.py             # Carga y preprocesamiento inicial de datos con Polars.
├── config.py             # Configuraciones de la aplicación (rutas de archivos, etc.).
├── eda.py                # Script para Análisis Exploratorio de Datos (opcional).
├── utils.py              # Funciones de utilidad (actualmente para EDA).
├── requirements.txt      # Dependencias del proyecto.
├── assets/               # Recursos gráficos (e.g., world_map.png, aunque no se usa activamente por Folium).
└── README.md             # Este archivo.
```

## 🔧 Configuración

Edita `config.py` para ajustar:
- Nombres de los archivos de datos (`LOCATION_FILE`, `USER_FILE`).
- `SAMPLE_SIZE`: Número de usuarios a muestrear para análisis más rápidos durante el desarrollo (usar `None` para el conjunto completo).
- `MAX_NODES_DISPLAY`: Límite de nodos a mostrar en el mapa Folium para mantener el rendimiento.

## 📊 Funcionalidades Detalladas (Implementaciones Manuales)

### Estructura del Grafo (`CustomGraph`)
- Representación interna mediante listas de adyacencia.
- Soporte para grafos dirigidos y no dirigidos (a través de conversión).
- Capacidad para manejar aristas ponderadas (utilizado en grafos agregados por Louvain).

### Análisis de Red
- **Nodos**: Usuarios de la red social.
- **Aristas**: Conexiones dirigidas (seguidor-seguido) en el grafo original.
- **Métricas Calculadas Manualmente**:
    - Número de nodos y aristas.
    - Densidad de la red.
    - Componentes conectados (usando BFS sobre grafo no dirigido).
    - Grado promedio.
    - Coeficiente de clustering promedio y local (usando conteo de triángulos sobre grafo no dirigido).

### Detección de Comunidades (Louvain)
- **Algoritmo**: Implementación manual del algoritmo de Louvain, que es un método jerárquico basado en la optimización de la modularidad.
- **Visualización**: Nodos coloreados en el mapa Folium según la comunidad detectada.
- **Estadísticas**: Número de comunidades, tamaño de las comunidades (se puede inferir de la partición).

### Análisis de Caminos (BFS)
- **Algoritmo**: Implementación manual de Breadth-First Search (BFS) para encontrar el camino más corto en términos de número de saltos (para grafos no ponderados).
- **Visualización**: El camino encontrado se resalta con una línea de color distintivo en el mapa Folium.

### Árbol de Expansión Mínima (Kruskal)
- **Algoritmo**: Implementación manual del algoritmo de Kruskal, utilizando una estructura Union-Find, para construir el MST (o un bosque si el grafo no es conectado). Se asumen pesos de arista 1 si no se especifica lo contrario para el grafo original.
- **Visualización**: Las aristas pertenecientes al MST se dibujan en el mapa Folium.

## 🎨 Interfaz de Usuario con Folium y Tkinter

### Panel Principal
- **Controles Superiores**: Botones para "Cargar Datos", "Detectar Comunidades", "Camino Más Corto", "Calcular MST", "Generar Estadísticas" y "Limpiar Visualización".
- **Panel Izquierdo (Mapa Folium)**: Muestra el mapa interactivo con los nodos, aristas (del camino/MST), y comunidades. Permite zoom, paneo y pop-ups con información al hacer clic en los nodos.
- **Panel Derecho (Información)**: Muestra estadísticas detalladas del grafo y de los análisis realizados.

## ⚡ Optimizaciones

- **Carga de Datos con Polars**: Para un manejo eficiente de archivos grandes.
- **Muestreo (`SAMPLE_SIZE`, `MAX_NODES_DISPLAY`)**: Opciones en `config.py` para trabajar con subconjuntos de datos y limitar la cantidad de nodos en el mapa, mejorando el rendimiento durante el desarrollo y análisis exploratorio.
- **Filtrado Geográfico Básico**: Se realiza un filtrado para excluir coordenadas evidentemente irreales (ej. en medio de océanos extensos).
- **Operaciones Asíncronas en GUI**: Las tareas de larga duración (carga de datos, análisis) se ejecutan en hilos separados para mantener la interfaz de usuario responsiva.
- **Implementaciones Manuales en Python**: Si bien educativas, las implementaciones manuales de algoritmos complejos como Louvain pueden ser menos performantes que las versiones optimizadas en C/C++ de bibliotecas especializadas, especialmente para grafos de 10 millones de nodos. La detección de comunidades en el conjunto completo puede ser intensiva en tiempo y memoria.

## 🔍 Análisis EDA Original (Opcional)

La aplicación permite ejecutar un Análisis Exploratorio de Datos (EDA) inicial a través del archivo `eda.py`. Este script (que usa Pandas, Matplotlib y Seaborn) genera:
- Histogramas de distribución de latitudes y longitudes.
- Análisis de outliers usando IQR.
- Estadísticas de conectividad por usuario (basado en el conteo de vecinos en el archivo de texto).
- Guarda las visualizaciones como archivos PNG.
Este EDA es independiente de los análisis principales realizados con los algoritmos manuales.

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**: Lenguaje principal.
- **Tkinter**: Para la estructura de la interfaz gráfica de usuario.
- **Folium**: Para la creación de mapas HTML interactivos.
- **tkhtmlview**: Para embeber los mapas Folium (HTML) dentro de la aplicación Tkinter.
- **Polars**: Para la carga y manipulación eficiente de datos tabulares grandes.
- **Pandas, Matplotlib, Seaborn**: Utilizados principalmente en el script `eda.py` para el análisis exploratorio de datos original.
- **Numpy**: Para operaciones numéricas.
- **psutil**: (Incluido en requisitos, puede usarse para monitoreo de sistema).

## 📝 Notas Importantes

- Los archivos de datos (`.txt`) deben estar en el directorio padre de `python_app` (ver sección de Instalación).
- La aplicación permite el muestreo de datos para un manejo más ágil con conjuntos de datos muy grandes.
- La funcionalidad completa de los algoritmos de Louvain y Kruskal depende de sus implementaciones manuales, que han sido desarrolladas como parte de este proyecto. Las implementaciones de algoritmos complejos como Louvain son intensivas y su rendimiento en Python puro para 10M de nodos puede ser limitado.

## 🤝 Contribuciones

Este proyecto es un esfuerzo por integrar el análisis de grafos, la implementación de algoritmos desde cero, y la visualización interactiva para el estudio de redes sociales masivas.

## 📄 Licencia

Proyecto académico.