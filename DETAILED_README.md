# Análisis de Red Social - Detalles Técnicos

Este documento proporciona una explicación detallada de los componentes internos, algoritmos y flujos de datos de la aplicación "Análisis de Red Social - Visualización de Grafos". Para una visión general, instalación y uso, consulta el [`README.md`](README.md) principal.

## 📁 Estructura Detallada del Proyecto y Componentes

El núcleo de la aplicación reside en el directorio `Ada Final LL/`.

```
TU_PROYECTO_RAIZ/
├── Ada Final LL/
│   ├── main.py               # Punto de entrada de la aplicación.
│   ├── gui_app.py            # Interfaz gráfica (Tkinter) y lógica de visualización (Folium).
│   ├── graph_analyzer.py     # Orquestación del análisis del grafo y manejo de datos.
│   ├── custom_graph.py       # Representación personalizada del grafo.
│   ├── algorithms.py         # Implementaciones manuales de algoritmos de grafos.
│   ├── loader.py             # Carga y preprocesamiento de datos con Polars.
│   ├── config.py             # Configuraciones de la aplicación.
│   ├── eda.py                # Script para Análisis Exploratorio de Datos (opcional).
│   ├── utils.py              # Funciones de utilidad (principalmente para EDA).
│   ├── requirements.txt      # Dependencias del proyecto.
│   └── ... (archivos generados como logs, imágenes, .pyc)
├── 10_million_location.txt   # Archivo de datos de ubicación (debe estar en la raíz).
└── 10_million_user.txt       # Archivo de datos de conexiones de usuarios (debe estar en la raíz).
└── README.md                 # README principal del proyecto.
└── DETAILED_README.md        # Este archivo.
```

---

### `Ada Final LL/main.py`

*   **Propósito Principal**: Punto de entrada de la aplicación. Inicializa y ejecuta la interfaz gráfica de usuario.
*   **Componentes Clave**:
    *   `main()`: Configura la ventana principal de Tkinter, instancia `SocialNetworkApp` y lanza el bucle principal de la GUI.
*   **Librerías Externas Usadas**:
    *   `tkinter`: Para crear la ventana raíz de la aplicación.
    *   `gui_app.py` (módulo local): Contiene la clase principal de la aplicación.
    *   `config.py` (módulo local): Para acceder a rutas de archivos y configuraciones.

---

### `Ada Final LL/gui_app.py`

*   **Propósito Principal**: Define la interfaz gráfica de usuario (GUI) utilizando Tkinter y gestiona la interacción del usuario, incluyendo la visualización de mapas con Folium.
*   **Componentes Clave**:
    *   `SocialNetworkApp` (Clase):
        *   `__init__(...)`: Inicializa la ventana, el `GraphAnalyzer`, y configura la UI.
        *   `setup_ui()`: Construye los elementos de la GUI (botones, campos de texto, paneles).
        *   `load_data_async()`, `_load_data_task()`: Manejan la carga de datos en un hilo separado para no bloquear la GUI.
        *   `detect_communities_async()`, `_detect_communities_task()`: Invocan la detección de comunidades en un hilo.
        *   `find_path_async()`, `_find_path_task()`: Invocan la búsqueda de caminos más cortos en un hilo.
        *   `calculate_mst_async()`, `_calculate_mst_task()`: Invocan el cálculo del MST en un hilo.
        *   `generate_analysis_async()`, `_generate_analysis_task()`, `_update_stats_display_from_analysis()`: Gestionan la generación y visualización de estadísticas del grafo.
        *   `_render_folium_map_to_html_widget()`: Genera un mapa Folium con nodos, aristas (caminos, MST) y comunidades, lo guarda como un archivo HTML temporal y lo abre en el navegador web predeterminado.
        *   `_update_map_visualization()`: Actualiza el mapa Folium cuando cambian los datos o selecciones.
        *   `update_status()`: Muestra mensajes de estado al usuario.
        *   `clear_visualization()`: Restablece la visualización y el estado de la aplicación.
*   **Librerías Externas Usadas**:
    *   `tkinter`: Para todos los elementos de la GUI.
    *   `folium`: Para generar los mapas interactivos.
    *   `webbrowser`: Para abrir los archivos HTML de Folium en el navegador.
    *   `threading`: Para ejecutar tareas pesadas (carga, análisis) en segundo plano.
    *   `polars` (indirectamente a través de `loader` y `graph_analyzer`): Para el manejo de datos.
    *   `numpy`: Para cálculos numéricos (ej. centroides de comunidades).
    *   `graph_analyzer.py`, `loader.py`, `config.py` (módulos locales).

---

### `Ada Final LL/graph_analyzer.py`

*   **Propósito Principal**: Clase central para el análisis del grafo. Carga datos procesados, construye el grafo, ejecuta algoritmos y calcula estadísticas.
*   **Componentes Clave**:
    *   `GraphAnalyzer` (Clase):
        *   `__init__()`: Inicializa el `CustomGraph`, y almacenamientos para ubicaciones, comunidades y MST.
        *   `load_data(locations_df, user_df, sample_size)`: Procesa DataFrames de Polars, filtra ubicaciones inválidas, aplica muestreo si se especifica, y construye el `CustomGraph` añadiendo nodos y aristas.
        *   `detect_communities(algorithm='louvain')`: Implementa la lógica para la detección de comunidades (actualmente enfocado en Louvain manual) y calcula propiedades de las comunidades.
        *   `find_shortest_path(start_node, end_node)`: Utiliza BFS (del módulo `algorithms`) para encontrar el camino más corto.
        *   `calculate_minimum_spanning_tree(algorithm_type='kruskal')`: Calcula el MST (actualmente enfocado en Kruskal manual).
        *   `get_density()`, `get_number_connected_components()`, `get_largest_connected_component_size()`, `get_average_clustering_coefficient()`: Calculan diversas métricas del grafo utilizando funciones del módulo `algorithms`.
        *   `analyze_geographic_distribution()`: Calcula estadísticas sobre la dispersión geográfica de los nodos.
        *   `get_node_info(node_id)`, `get_top_connected_nodes(n)`: Recuperan información específica de nodos.
*   **Librerías Externas Usadas**:
    *   `numpy`: Para cálculos (ej. promedios en detección de comunidades).
    *   `polars`: Para interactuar con los DataFrames pasados desde `loader`.
    *   `custom_graph.py` (módulo local): Para la instancia del grafo.
    *   `algorithms.py` (módulo local): Para las implementaciones de los algoritmos.

---

### `Ada Final LL/custom_graph.py`

*   **Propósito Principal**: Define una estructura de datos de grafo personalizada.
*   **Componentes Clave**:
    *   `CustomGraph` (Clase):
        *   `__init__()`: Inicializa `adj` (lista de adyacencia para sucesores), `pred` (lista de adyacencia para predecesores) y `nodes` (conjunto de nodos).
        *   `add_node(node_id)`: Añade un nodo.
        *   `add_edge(u, v, weight=1.0)`: Añade una arista dirigida de `u` a `v` con un peso.
        *   `get_nodes()`, `get_edges(data=False)`: Devuelven nodos y aristas.
        *   `get_neighbors(node_id)`, `get_predecessors(node_id)`: Devuelven vecinos y predecesores.
        *   `degree(node_id)`, `in_degree(node_id)`, `out_degree(node_id)`: Calculan grados.
        *   `number_of_nodes()`, `number_of_edges()`: Devuelven el tamaño del grafo.
        *   `to_undirected()`: Crea una versión no dirigida del grafo.
*   **Librerías Externas Usadas**:
    *   `collections.defaultdict`: Para las listas de adyacencia.

---

### `Ada Final LL/algorithms.py`

*   **Propósito Principal**: Contiene las implementaciones manuales de los algoritmos de grafos utilizados en la aplicación.
*   **Componentes Clave (Funciones)**:
    *   `bfs_shortest_path(graph, start_node, end_node)`: Implementación de Breadth-First Search para caminos más cortos en grafos no ponderados.
    *   `calculate_density(graph_undirected)`: Calcula la densidad de un grafo.
    *   `get_connected_components(graph_undirected)`: Encuentra todos los componentes conectados.
    *   `local_clustering_coefficient(graph_undirected, node_id)`, `average_clustering_coefficient(graph_undirected)`: Calculan el coeficiente de clustering.
    *   `detect_communities_louvain(graph_input)`: Implementación manual del algoritmo de Louvain para detección de comunidades. Incluye fases de optimización de modularidad y agregación de la red.
        *   `_calculate_modularity(...)`, `_build_community_graph(...)`: Funciones auxiliares para Louvain.
    *   `UnionFind` (Clase): Estructura de datos para el seguimiento de conjuntos disjuntos, utilizada por Kruskal.
        *   `find(node)`, `union(node1, node2)`: Operaciones estándar de Union-Find.
    *   `minimum_spanning_tree_kruskal(graph_undirected_weighted)`: Implementación manual del algoritmo de Kruskal para encontrar el Árbol de Expansión Mínima (MST).
*   **Librerías Externas Usadas**:
    *   `collections.deque`, `collections.defaultdict`: Para estructuras de datos eficientes.
    *   `custom_graph.py` (módulo local): Para interactuar con la estructura del grafo.

---

### `Ada Final LL/loader.py`

*   **Propósito Principal**: Maneja la carga y el preprocesamiento inicial de los archivos de datos de entrada.
*   **Componentes Clave (Funciones)**:
    *   `load_location_data(filepath)`: Carga el archivo de ubicaciones, lo interpreta como CSV, añade un ID de nodo basado en el índice de fila y convierte las coordenadas a flotantes.
    *   `load_user_data(filepath)`: Carga el archivo de conexiones de usuarios, tratando cada línea como una lista de adyacencia en formato de cadena.
*   **Librerías Externas Usadas**:
    *   `polars`: Para leer y procesar eficientemente los archivos CSV y de texto como DataFrames.
    *   `os`: Para comprobaciones de existencia de archivos.

---

### `Ada Final LL/config.py`

*   **Propósito Principal**: Almacena configuraciones globales para la aplicación.
*   **Componentes Clave (Variables Globales)**:
    *   `LOCATION_FILE`, `USER_FILE`: Nombres de los archivos de datos.
    *   `APP_TITLE`, `WINDOW_WIDTH`, `WINDOW_HEIGHT`: Configuraciones de la GUI.
    *   `MAX_NODES_DISPLAY`: Límite de nodos a mostrar en el mapa Folium (puede ser `None`).
    *   `SAMPLE_SIZE`: Número de nodos a muestrear del conjunto de datos total para análisis y visualización (puede ser `None` para usar todos los datos).
    *   `MAX_PATH_NODES`: Límite de nodos para visualización en caminos (puede ser `None`).

---

### `Ada Final LL/eda.py` (Análisis Exploratorio de Datos Opcional)

*   **Propósito Principal**: Script independiente para realizar un Análisis Exploratorio de Datos (EDA) básico sobre los archivos de entrada. No es parte integral del flujo principal de la aplicación GUI.
*   **Componentes Clave**:
    *   Funciones para cargar datos (usando Pandas en este script).
    *   Generación de histogramas para distribuciones de latitud y longitud.
    *   Análisis de outliers.
    *   Estadísticas básicas de conectividad.
*   **Librerías Externas Usadas**:
    *   `pandas`: Para la manipulación de datos en este script.
    *   `matplotlib`, `seaborn`: Para la generación de gráficos.
    *   `numpy`: Para cálculos.
    *   `utils.py` (módulo local): Puede contener funciones auxiliares para el EDA.

---

### `Ada Final LL/utils.py`

*   **Propósito Principal**: Contiene funciones de utilidad general. En el estado actual, parece estar más orientado a ayudar al script `eda.py`.
*   **Componentes Clave**:
    *   (Depende del contenido actual, que no se ha inspeccionado en detalle, pero podría incluir funciones para guardar gráficos, calcular IQR, etc.)
*   **Librerías Externas Usadas**:
    *   Potencialmente `matplotlib`, `numpy`.

## ⚙️ Algoritmos Implementados

Una característica central de este proyecto es la implementación manual de varios algoritmos de análisis de grafos.

### 1. Búsqueda de Caminos (BFS - Breadth-First Search)
*   **Ubicación**: `Ada Final LL/algorithms.py` -> `bfs_shortest_path()`
*   **Descripción**: BFS es un algoritmo para recorrer o buscar estructuras de datos de árbol o grafo. Comienza en la raíz (o un nodo arbitrario) y explora todos los nodos vecinos a la profundidad actual antes de moverse a los nodos en el siguiente nivel de profundidad.
*   **Uso en la Aplicación**: Se utiliza para encontrar el camino más corto (en términos de número de aristas) entre dos nodos seleccionados por el usuario en el grafo de la red social. El grafo se trata como no ponderado para este propósito.
*   **Características**:
    *   Garantiza encontrar el camino más corto en grafos no ponderados.
    *   Implementado usando una cola (`collections.deque`).

### 2. Detección de Comunidades (Louvain)
*   **Ubicación**: `Ada Final LL/algorithms.py` -> `detect_communities_louvain()`
*   **Descripción**: El algoritmo de Louvain es un método greedy de optimización de la modularidad para detectar comunidades en redes grandes. Opera en dos fases repetitivas:
    1.  **Optimización de Modularidad Local**: Para cada nodo, se considera moverlo a una comunidad vecina. El nodo se coloca en la comunidad que resulta en el mayor aumento de modularidad. Esto se repite hasta que no se puedan realizar movimientos que mejoren la modularidad.
    2.  **Agregación de la Red**: Se construye un nuevo grafo donde los nodos son las comunidades encontradas en la Fase 1. Las aristas entre los nuevos nodos se ponderan según la suma de los pesos de las aristas entre nodos en las comunidades correspondientes.
    Estas fases se repiten hasta que la modularidad máxima no pueda aumentarse más.
*   **Uso en la Aplicación**: Identifica grupos de usuarios densamente conectados (comunidades) dentro de la red social.
*   **Características**:
    *   Implementación manual que sigue las fases principales del algoritmo.
    *   Calcula la modularidad para guiar la formación de comunidades.
    *   Maneja grafos ponderados (útil para los niveles agregados).

### 3. Árbol de Expansión Mínima (MST - Kruskal)
*   **Ubicación**: `Ada Final LL/algorithms.py` -> `minimum_spanning_tree_kruskal()`
*   **Descripción**: El algoritmo de Kruskal encuentra un subconjunto de las aristas de un grafo conectado y no dirigido que conecta todos los vértices sin formar ciclos y con el mínimo peso total de aristas posible.
    1.  Ordena todas las aristas del grafo por peso en orden ascendente.
    2.  Itera sobre las aristas ordenadas. Si una arista conecta dos componentes previamente desconectados (es decir, no forma un ciclo con las aristas ya seleccionadas), se añade al MST.
    3.  Esto se realiza eficientemente usando una estructura de datos Union-Find.
*   **Uso en la Aplicación**: Puede visualizar la "columna vertebral" de la red. Para el grafo original no ponderado, conecta todos los nodos (o componentes) con el menor número de aristas.
*   **Características**:
    *   Implementación manual que utiliza una clase `UnionFind` (también implementada manualmente).
    *   Funciona sobre una versión no dirigida del grafo. Si el grafo original es no ponderado, todas las aristas tienen peso implícito 1.

### 4. Estructura de Datos Union-Find
*   **Ubicación**: `Ada Final LL/algorithms.py` -> `UnionFind` (Clase)
*   **Descripción**: Una estructura de datos que realiza un seguimiento de un conjunto de elementos particionados en varios subconjuntos disjuntos (no superpuestos). Proporciona dos operaciones principales:
    *   `find(item)`: Determina a qué subconjunto pertenece un elemento particular. Puede devolver un "representante" o "raíz" de ese subconjunto.
    *   `union(set1, set2)`: Une dos subconjuntos en un solo subconjunto.
*   **Uso en la Aplicación**: Esencial para la implementación eficiente del algoritmo de Kruskal, para verificar si añadir una arista crearía un ciclo.
*   **Características**:
    *   Implementa optimizaciones como la unión por tamaño/rango y la compresión de caminos para mejorar la eficiencia.

### 5. Métricas de Grafo Adicionales
*   **Ubicación**: `Ada Final LL/algorithms.py`
*   **Funciones**:
    *   `calculate_density()`: Mide cuán conectado está el grafo en relación con el máximo número posible de aristas.
    *   `get_connected_components()`: Identifica subgrafos en los que cualquier par de nodos está conectado entre sí por caminos.
    *   `local_clustering_coefficient()`, `average_clustering_coefficient()`: Miden la tendencia de los nodos en un grafo a agruparse. El coeficiente local para un nodo es la proporción de aristas entre sus vecinos dividida por el número de pares de vecinos.

## 💾 Manejo de Datos

### Archivos de Entrada
La aplicación espera dos archivos de texto principales, que deben estar ubicados en el directorio raíz del proyecto (el directorio que contiene la carpeta `Ada Final LL/`):

1.  **Archivo de Ubicaciones** (ej. `10_million_location.txt`, configurable en `config.py`):
    *   **Formato**: Cada línea representa un nodo y contiene `latitud,longitud`.
        ```
        34.0522,-118.2437
        40.7128,-74.0060
        ...
        ```
    *   **ID de Nodo**: El ID del nodo se infiere implícitamente del número de línea (0-indexado). La primera línea corresponde al nodo 0, la segunda al nodo 1, y así sucesivamente.
    *   **Procesamiento**: Cargado por `loader.load_location_data()` usando Polars. Se añade una columna 'id'.

2.  **Archivo de Usuarios/Conexiones** (ej. `10_million_user.txt`, configurable en `config.py`):
    *   **Formato**: Cada línea representa las conexiones salientes de un nodo. El número de línea (0-indexado) corresponde al ID del nodo de origen. El contenido de la línea es una lista de IDs de nodos destino, separados por espacios o comas.
        ```
        1 2 3
        0 2
        0 1 5 
        ...
        ```
        La primera línea (nodo 0) se conecta a los nodos 1, 2 y 3. La segunda línea (nodo 1) se conecta a los nodos 0 y 2.
    *   **Procesamiento**: Cargado por `loader.load_user_data()` usando Polars. Cada línea se lee como una cadena. El `GraphAnalyzer` luego parsea estas cadenas para construir las aristas del grafo.

### Proceso de Carga y Construcción del Grafo (`GraphAnalyzer.load_data`)
1.  Los DataFrames de Polars (de `loader.py`) se pasan a `GraphAnalyzer`.
2.  **Ubicaciones**: Se itera sobre el DataFrame de ubicaciones. Las coordenadas se validan (`_is_valid_location`). Las ubicaciones válidas se almacenan en `self.locations = {node_id: (lat, lng)}`. Se crea un conjunto `valid_node_ids`.
3.  **Muestreo (`SAMPLE_SIZE`)**: Si `SAMPLE_SIZE` está definido en `config.py` y es menor que el número de nodos válidos, se toma una muestra aleatoria de `valid_node_ids` para formar `nodes_to_consider_for_graph`. `self.locations` se filtra para contener solo nodos muestreados.
4.  **Construcción del Grafo**:
    *   Se inicializa un nuevo `CustomGraph`.
    *   Se itera sobre el DataFrame de usuarios. El índice de la fila es el `current_node_original_id`.
    *   Si `current_node_original_id` está en `nodes_to_consider_for_graph`:
        *   Se añade el nodo al grafo.
        *   Se parsea su lista de adyacencia (cadena de texto).
        *   Para cada `neighbor_id` en la lista:
            *   Si `neighbor_id` también está en `nodes_to_consider_for_graph`, se añade el vecino como nodo (si no existe ya) y se añade una arista dirigida de `current_node_original_id` a `neighbor_id`.

## 🖥️ Visualización con Folium

*   **Generación de Mapas**: La función `_render_folium_map_to_html_widget` en `gui_app.py` es responsable de crear los mapas.
*   **Funcionamiento**:
    1.  Se crea un objeto `folium.Map`, centrado geográficamente basado en las ubicaciones de los nodos.
    2.  Los nodos (con ubicaciones válidas y que están en el grafo, posiblemente muestreados por `MAX_NODES_DISPLAY`) se dibujan como `folium.CircleMarker`.
        *   Los pop-ups de los marcadores muestran el ID del nodo y sus coordenadas.
        *   El color de los marcadores puede cambiar para indicar comunidades o si son parte de un camino seleccionado.
    3.  **Caminos**: Si se encuentra un camino más corto, se dibuja como una `folium.PolyLine` conectando los nodos del camino.
    4.  **MST**: Si se calcula un MST, sus aristas también se dibujan como `folium.PolyLine`.
    5.  **Comunidades**: Los nodos se colorean según la comunidad detectada.
*   **Salida**: El mapa Folium se guarda como un archivo HTML temporal.
*   **Visualización**: `webbrowser.open()` se utiliza para abrir este archivo HTML en el navegador web predeterminado del usuario. Cada nueva visualización o actualización del mapa generalmente abrirá una nueva pestaña o reutilizará una existente, dependiendo del navegador y la configuración de `webbrowser.open(..., new=...)`.

## 💡 Optimizaciones y Consideraciones de Rendimiento

*   **Polars para Carga**: El uso de Polars en `loader.py` es significativamente más rápido y consume menos memoria que Pandas para la carga inicial de archivos grandes.
*   **Muestreo (`SAMPLE_SIZE`, `MAX_NODES_DISPLAY`)**: Permite trabajar con conjuntos de datos muy grandes de manera más ágil durante el desarrollo o para análisis rápidos, al reducir el número de nodos y aristas procesados y visualizados.
*   **Operaciones Asíncronas en GUI**: Las tareas de larga duración (carga de datos, ejecución de algoritmos) se realizan en hilos (`threading`) para evitar que la interfaz de usuario se congele.
*   **Implementaciones Manuales**: Si bien son valiosas desde una perspectiva de aprendizaje, las implementaciones de algoritmos complejos en Python puro (como Louvain) pueden ser órdenes de magnitud más lentas que las implementaciones optimizadas en lenguajes de más bajo nivel (C, C++, Rust) que se encuentran en bibliotecas de grafos establecidas (ej. NetworkX, igraph, graph-tool). Para grafos del tamaño de "10 millones de nodos", la ejecución de Louvain manual en el conjunto completo puede ser muy prolongada.
*   **Visualización de Folium**: Renderizar decenas de miles de marcadores y líneas en Folium puede volverse lento en el navegador. `MAX_NODES_DISPLAY` ayuda a mitigar esto. `FastMarkerCluster` (comentado en el código) podría ser una opción para mejorar el rendimiento con muchos marcadores si se decide usarla.

Este documento debería proporcionar una comprensión profunda de cómo funciona internamente la aplicación.
