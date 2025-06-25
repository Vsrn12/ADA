import numpy as np
from collections import defaultdict, deque
import heapq # Puede ser útil para Dijkstra o Prim
# from sklearn.cluster import KMeans # Comentado
import logging
import polars as pl
from custom_graph import CustomGraph
import algorithms # Importar el nuevo módulo de algoritmos

class GraphAnalyzer:
    def __init__(self):
        self.locations = {} # Diccionario: {node_id: (lat, lng)}
        self.graph = CustomGraph() # Usar la clase de grafo personalizada
        self.communities = {} # Diccionario: {community_id: {'nodes': set(), 'center_lat': ..., 'center_lng': ...}}
        self.mst = None # Atributo para almacenar el Árbol de Expansión Mínima (CustomGraph)

    def _is_valid_location(self, lat, lng):
        """
        Verifica si las coordenadas están dentro de rangos geográficos válidos
        y filtra algunas áreas oceánicas o irreales comunes.
        """
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return False
        # Filtros heurísticos para áreas oceánicas o de datos anómalos
        if -30 < lat < 30 and 160 < lng < -120: # Pacífico Central
            return False
        if -30 < lat < 30 and -40 < lng < -10: # Atlántico Central
            return False
        if -30 < lat < 10 and 60 < lng < 100: # Océano Índico
            return False
        return True
        
    def load_data(self, locations_df: pl.DataFrame, user_df: pl.DataFrame, sample_size=None):
        """
        Carga y procesa los datos de ubicación y usuario para construir el grafo.
        Ahora recibe DataFrames de Polars ya cargados.
        """
        logging.info("Iniciando procesamiento de DataFrames en GraphAnalyzer...")

        self.locations = {}
        valid_node_ids = set()

        # Procesar locations_df
        # Asumiendo que locations_df tiene columnas 'lat' y 'long'
        # Y que el índice de la fila (0-indexed) corresponde al ID de usuario/nodo
        for i, row_values in enumerate(locations_df.iter_rows()):
            # locations_df tiene columnas: "id", "lat", "long" en ese orden.
            # row_values será una tupla: (id_val, lat_val, long_val)
            # El índice 'i' de enumerate corresponde al 'id_val' y es el ID del nodo.
            node_id = i # o row_values[0], ambos deben ser iguales. Usar i es más directo.
            lat = row_values[1] 
            lng = row_values[2]
            
            if self._is_valid_location(lat, lng):
                self.locations[node_id] = (lat, lng) # Guardar como (lat, lng)
                valid_node_ids.add(i)
        
        logging.info(f"Ubicaciones válidas procesadas: {len(self.locations)}.")

        # Procesar user_df (listas de adyacencia)
        self.graph = CustomGraph() # Reiniciar el grafo

        # Determinar el conjunto final de nodos a incluir en el grafo
        nodes_to_consider_for_graph = valid_node_ids # Por defecto, todos los nodos con ubicación válida

        if sample_size is not None and len(valid_node_ids) > sample_size:
            logging.info(f"Se aplicará un muestreo para limitar el grafo a aproximadamente {sample_size} nodos.")
            # Tomar una muestra aleatoria de los nodos que tienen ubicaciones válidas
            # Convertir set a list para np.random.choice
            potential_nodes_list = list(valid_node_ids)
            # Asegurarse de no pedir más muestras de las disponibles
            actual_sample_size = min(sample_size, len(potential_nodes_list))
            sampled_node_ids = set(np.random.choice(potential_nodes_list, actual_sample_size, replace=False))
            nodes_to_consider_for_graph = sampled_node_ids
            logging.info(f"Muestreo realizado. Se considerarán {len(nodes_to_consider_for_graph)} nodos para el grafo.")

            # Filtrar self.locations para que solo contenga los nodos muestreados
            self.locations = {node_id: loc for node_id, loc in self.locations.items() if node_id in nodes_to_consider_for_graph}
            logging.info(f"Diccionario de ubicaciones filtrado a {len(self.locations)} entradas post-muestreo.")

        # Construir el grafo
        # Iterar sobre el user_df original. El índice 'i' es el ID original del nodo.
        for i, adj_row in enumerate(user_df.iter_rows(named=True)): # Asumiendo que 'adj_list' es el nombre de la columna
            current_node_original_id = i 
            adj_str = adj_row['adj_list']

            if current_node_original_id in nodes_to_consider_for_graph:
                self.graph.add_node(current_node_original_id) # Añadir nodo al grafo

                if adj_str: # Asegurarse de que la cadena no esté vacía
                    try:
                        neighbors_str_list = adj_str.replace(',', ' ').split()
                        original_neighbor_ids = [int(n) for n in neighbors_str_list if n.isdigit()]
                        
                        for neighbor_id in original_neighbor_ids:
                            # Añadir arista solo si el vecino también está en el conjunto de nodos a considerar
                            if neighbor_id in nodes_to_consider_for_graph:
                                self.graph.add_node(neighbor_id) # Asegurar que el vecino también esté como nodo
                                self.graph.add_edge(current_node_original_id, neighbor_id)
                    except ValueError as ve:
                        logging.warning(f"Error al parsear lista de adyacencia para el nodo {current_node_original_id}: {ve}. Línea: '{adj_str}'")
            
        logging.info(f"Grafo construido con {self.graph.number_of_nodes()} nodos y {self.graph.number_of_edges()} aristas.")
        self.communities = {} # Reset communities on new data load

    def detect_communities(self, algorithm='louvain', random_state=42):
        """
        Detecta comunidades en el grafo y calcula el centro geográfico para cada una.
        Soporta 'louvain' (requiere python-louvain) o 'kmeans' (más simple, basado en geolocalización).
        """
        if not self.graph.number_of_nodes() > 0:
            logging.warning("No hay nodos en el grafo para detectar comunidades.")
            self.communities = {}
            return

        logging.info(f"Detectando comunidades usando el algoritmo: {algorithm}...")
        self.communities = {} # Limpiar comunidades anteriores

        if algorithm == 'louvain':
            partition = algorithms.detect_communities_louvain(self.graph) # Llamar a la implementación manual
            
            if not partition:
                logging.warning("Louvain manual no devolvió una partición válida.")
                self.communities = {}
                return

            # Agrupar nodos por comunidad y calcular centro geográfico
            # Esta parte de la lógica se puede reutilizar si la 'partition' tiene el formato {node: community_id}
            community_nodes_map = defaultdict(list)
            for node, comm_id in partition.items():
                community_nodes_map[comm_id].append(node)
            
            for comm_id, nodes_in_comm in community_nodes_map.items():
                nodes_with_location = [node for node in nodes_in_comm if node in self.locations]
                
                if nodes_with_location:
                    lats = [self.locations[node][0] for node in nodes_with_location]
                    lngs = [self.locations[node][1] for node in nodes_with_location]
                    
                    center_lat = np.mean(lats) if lats else 0.0
                    center_lng = np.mean(lngs) if lngs else 0.0
                    
                    self.communities[comm_id] = {
                        'nodes': set(nodes_in_comm),
                        'size': len(nodes_in_comm),
                        'center_lat': center_lat,
                        'center_lng': center_lng
                    }
                else:
                    # Aún crear la comunidad pero sin centro geo si no hay nodos con ubicación
                    self.communities[comm_id] = {
                        'nodes': set(nodes_in_comm),
                        'size': len(nodes_in_comm),
                        'center_lat': None,
                        'center_lng': None
                    }
                    logging.warning(f"Comunidad {comm_id} (Louvain manual) no tiene nodos con ubicaciones válidas para calcular el centro.")
            
            logging.info(f"Detección de comunidades Louvain (manual placeholder) completada. Encontradas {len(self.communities)} comunidades.")
            # try:
            #     # import community as co # python-louvain library # ESTO SE ELIMINARÁ
            #     # partition = co.best_partition(self.graph.to_undirected_nx()) # Louvain works on undirected graphs
                
            #     # # Agrupar nodos por comunidad y calcular centro
            #     # community_nodes = defaultdict(list)
            #     # for node, comm_id in partition.items():
            #     #     community_nodes[comm_id].append(node)
                
            #     # for comm_id, nodes_in_comm in community_nodes.items():
            #     #     # Filtrar nodos que realmente tienen ubicación
            #     #     nodes_with_location = [node for node in nodes_in_comm if node in self.locations]
                    
            #     #     if nodes_with_location:
            #     #         lats = [self.locations[node][0] for node in nodes_with_location]
            #     #         lngs = [self.locations[node][1] for node in nodes_with_location]
                        
            #     #         center_lat = np.mean(lats) if lats else 0
            #     #         center_lng = np.mean(lngs) if lngs else 0
                        
            #     #         self.communities[comm_id] = {
            #     #             'nodes': set(nodes_in_comm), # Mantener todos los nodos de la partición Louvain
            #     #             'size': len(nodes_in_comm),
            #     #             'center_lat': center_lat,
            #     #             'center_lng': center_lng
            #     #         }
            #     #     else:
            #     #         logging.warning(f"Comunidad {comm_id} no tiene nodos con ubicaciones válidas.")

            #     # logging.info(f"Detección de comunidades Louvain completada. Encontradas {len(self.communities)} comunidades.")
            #     pass # Placeholder para la implementación manual

            # except ImportError:
            #     logging.error("La librería 'python-louvain' no está instalada. No se puede usar el algoritmo Louvain.")
            #     self.communities = {}
            # except Exception as e:
            #     logging.error(f"Error durante la detección de comunidades Louvain: {e}")
            #     self.communities = {}
            pass # Fin del bloque Louvain
        
        elif algorithm == 'kmeans':
            # K-means no es un algoritmo de detección de comunidades basado en la estructura de red típicamente.
            # Se mantendrá comentado o se eliminará si no es un requisito principal.
            logging.warning("El algoritmo K-means para comunidades es experimental y está basado en geolocalización, no en estructura de red.")
            
        else:
            logging.warning(f"Algoritmo de comunidad '{algorithm}' no reconocido o no implementado manualmente aún.")

    def find_shortest_path(self, start_node, end_node):
        """
        Encuentra el camino más corto entre dos nodos.
        Este método será reemplazado por una implementación manual de BFS/Dijkstra.
        """
        if start_node not in self.graph.get_nodes() or end_node not in self.graph.get_nodes(): # Usa CustomGraph
            logging.warning(f"Uno o ambos nodos ({start_node}, {end_node}) no existen en el grafo.")
            return None
        
        # Placeholder para la implementación manual de BFS/Dijkstra
        # path = self._bfs(start_node, end_node) # Ejemplo si BFS se implementa como método privado
        # if path:
        #    logging.info(f"Camino encontrado entre {start_node} y {end_node}: {path}")
        #    return path
        # else:
        #    logging.warning(f"No se encontró un camino entre {start_node} y {end_node}.")
        #    return None
        # logging.info(f"Búsqueda de camino más corto manual para {start_node} -> {end_node} (AÚN NO IMPLEMENTADO).")
        # return None # Temporalmente devuelve None
        path = algorithms.bfs_shortest_path(self.graph, start_node, end_node)
        if path:
            logging.info(f"Camino encontrado (BFS manual) entre {start_node} y {end_node}: {path}")
        else:
            logging.warning(f"No se encontró camino (BFS manual) entre {start_node} y {end_node}.")
        return path

    def get_path_distance(self, path):
        """Calcula la distancia de un camino (número de aristas)."""
        if path and len(path) > 1:
            return len(path) - 1
        return 0

    def get_node_info(self, node_id):
        """Obtener información detallada de un nodo."""
        if node_id not in self.graph.get_nodes(): # Usa CustomGraph
            logging.warning(f"Nodo {node_id} no encontrado en el grafo para get_node_info.")
            return None
            
        info = {
            'id': node_id,
            'location': self.locations.get(node_id, (0, 0)), # Esto permanece igual
            'degree': self.graph.degree(node_id),             # Usa CustomGraph
            'in_degree': self.graph.in_degree(node_id),       # Usa CustomGraph
            'out_degree': self.graph.out_degree(node_id),     # Usa CustomGraph
            'neighbors': list(self.graph.get_neighbors(node_id)), # Usa CustomGraph
            'community': None # Esto se llenará cuando se implemente la detección de comunidades
        }
        
        # Encontrar comunidad (esta lógica se mantendrá una vez que self.communities se llene)
        for comm_id, comm_data in self.communities.items():
            if node_id in comm_data['nodes'] and comm_id is not None: # Ensure comm_id is not None
                info['community'] = comm_id
                break
                
        return info
    
    def get_top_connected_nodes(self, n=10):
        """Obtener los nodos más conectados (por grado)"""
        if not self.graph.number_of_nodes() > 0: # Usa CustomGraph
            return []
        
        # Obtener todos los grados y luego ordenar
        degrees = []
        for node in self.graph.get_nodes(): # Usa CustomGraph
            degrees.append((node, self.graph.degree(node))) # Usa CustomGraph
            
        degrees.sort(key=lambda x: x[1], reverse=True)
        return degrees[:n]
    
    def get_density(self):
        """Devuelve la densidad del grafo."""
        return algorithms.calculate_density(self.graph)

    def get_number_connected_components(self):
        """Devuelve el número de componentes conectados (para grafo no dirigido)."""
        undirected_graph = self.graph.to_undirected()
        components = algorithms.get_connected_components(undirected_graph)
        return len(components)

    def get_largest_connected_component_size(self):
        """Devuelve el tamaño del componente conectado más grande (para grafo no dirigido)."""
        undirected_graph = self.graph.to_undirected()
        components = algorithms.get_connected_components(undirected_graph)
        if not components:
            return 0
        return max(len(c) for c in components)

    def get_average_clustering_coefficient(self):
        """Devuelve el coeficiente de clustering promedio (para grafo no dirigido)."""
        undirected_graph = self.graph.to_undirected()
        return algorithms.average_clustering_coefficient(undirected_graph)

    def calculate_minimum_spanning_tree(self, algorithm_type='kruskal'):
        """
        Calcula el Árbol de Expansión Mínima (MST) del grafo.
        El grafo se considera no dirigido y las aristas con peso 1.
        """
        if self.graph.number_of_nodes() == 0:
            logging.warning("No hay nodos en el grafo para calcular el MST.")
            self.mst = CustomGraph() # MST vacío
            return self.mst

        undirected_graph = self.graph.to_undirected()
        
        if algorithm_type == 'kruskal':
            # Asumimos que kruskal en algorithms.py puede manejar un grafo CustomGraph no ponderado
            # o que se adapta para tomar pesos si CustomGraph los soporta en el futuro.
            logging.info("Calculando MST usando Kruskal (manual placeholder)...")
            self.mst = algorithms.minimum_spanning_tree_kruskal(undirected_graph)
        # elif algorithm_type == 'prim':
            # self.mst = algorithms.minimum_spanning_tree_prim(undirected_graph) # Si se implementa Prim
        else:
            logging.warning(f"Algoritmo MST '{algorithm_type}' no reconocido o no implementado.")
            self.mst = CustomGraph() # Devuelve un grafo vacío si el algoritmo no es válido
        
        if self.mst and self.mst.number_of_edges() > 0:
            logging.info(f"MST calculado con {self.mst.number_of_nodes()} nodos y {self.mst.number_of_edges()} aristas.")
        elif self.mst:
            logging.info("MST calculado, pero resultó en un grafo vacío (posiblemente el grafo original estaba vacío o desconectado de una manera particular para Kruskal).")
        
        return self.mst
    
    def analyze_geographic_distribution(self):
        """Analizar distribución geográfica de nodos"""
        if not self.locations:
            return {}
            
        lats = [loc[0] for loc in self.locations.values()]
        lngs = [loc[1] for loc in self.locations.values()]
        
        if not lats or not lngs: # Handle case where all locations might be invalid after filtering
            return {}

        return {
            'lat_range': (min(lats), max(lats)),
            'lng_range': (min(lngs), max(lngs)),
            'lat_center': np.mean(lats),
            'lng_center': np.mean(lngs)
        }