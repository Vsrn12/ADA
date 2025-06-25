from collections import defaultdict

class CustomGraph:
    """
    Una implementación de un grafo dirigido simple usando listas de adyacencia.
    """
    def __init__(self):
        self.adj = defaultdict(dict) # Diccionario para sucesores: {u: {v1: weight1, v2: weight2}}
        self.pred = defaultdict(dict) # Diccionario para predecesores: {v: {u1: weight1, u2: weight2}}
        self.nodes = set()            # Conjunto de todos los nodos en el grafo

    def add_node(self, node_id):
        """Añade un nodo al grafo."""
        if node_id not in self.nodes:
            self.nodes.add(node_id)
            # Asegura que el nodo exista como clave en adj y pred
            _ = self.adj[node_id] 
            _ = self.pred[node_id]


    def add_edge(self, u, v, weight=1.0):
        """Añade una arista dirigida de u a v con un peso opcional."""
        self.add_node(u)
        self.add_node(v)
        
        self.adj[u][v] = weight
        self.pred[v][u] = weight

    def get_nodes(self):
        """Devuelve un conjunto de todos los nodos."""
        return self.nodes

    def get_edges(self, data=False):
        """
        Devuelve una lista de todas las aristas.
        Si data es True, devuelve tuplas (u, v, weight).
        Sino, devuelve tuplas (u,v).
        """
        edges = []
        for u, neighbors_dict in self.adj.items():
            for v, weight in neighbors_dict.items():
                if data:
                    edges.append((u, v, weight))
                else:
                    edges.append((u, v))
        return edges

    def get_edge_weight(self, u, v):
        """Devuelve el peso de la arista (u,v). Lanza KeyError si la arista no existe."""
        if u not in self.adj or v not in self.adj[u]:
            # Opcional: devolver un peso por defecto (e.g., 0 o None) o lanzar error
            raise KeyError(f"Arista ({u},{v}) no encontrada.")
        return self.adj[u][v]

    def get_neighbors(self, node_id):
        """Devuelve un conjunto de sucesores (nodos) del nodo_id."""
        if node_id not in self.nodes:
            return set()
        return set(self.adj[node_id].keys()) # Solo los nodos, no los pesos

    def get_predecessors(self, node_id):
        """Devuelve un conjunto de predecesores (nodos) del nodo_id."""
        if node_id not in self.nodes:
            return set()
        return set(self.pred[node_id].keys()) # Solo los nodos

    def degree(self, node_id, weighted=False):
        """
        Devuelve el grado total (entrada + salida) del nodo_id.
        Si weighted es True, devuelve la suma de pesos de las aristas (fuerza).
        """
        if node_id not in self.nodes:
            return 0
        return self.in_degree(node_id, weighted=weighted) + self.out_degree(node_id, weighted=weighted)

    def in_degree(self, node_id, weighted=False):
        """
        Devuelve el grado de entrada del nodo_id.
        Si weighted es True, devuelve la suma de pesos de las aristas entrantes.
        """
        if node_id not in self.nodes:
            return 0
        if weighted:
            return sum(self.pred[node_id].values())
        return len(self.pred[node_id])

    def out_degree(self, node_id, weighted=False):
        """
        Devuelve el grado de salida del nodo_id.
        Si weighted es True, devuelve la suma de pesos de las aristas salientes.
        """
        if node_id not in self.nodes:
            return 0
        if weighted:
            return sum(self.adj[node_id].values())
        return len(self.adj[node_id])

    def number_of_nodes(self):
        """Devuelve el número total de nodos."""
        return len(self.nodes)

    def number_of_edges(self):
        """Devuelve el número total de aristas."""
        count = 0
        for node in self.adj:
            count += len(self.adj[node])
        return count

    def to_undirected(self):
        """
        Crea una versión no dirigida de este grafo.
        En un grafo no dirigido, si hay una arista u -> v, también hay v -> u.
        """
        undirected_graph = CustomGraph()
        for u in self.nodes:
            undirected_graph.add_node(u)
        
        for u, neighbors in self.adj.items():
            for v in neighbors:
                undirected_graph.add_edge(u, v)
                undirected_graph.add_edge(v, u) # Asegura la reciprocidad
        return undirected_graph

    def get_node_attributes(self, node_id, locations_map):
        """
        Obtiene atributos básicos de un nodo.
        Similar a get_node_info pero sin la parte de comunidad por ahora.
        """
        if node_id not in self.nodes:
            return None
        
        info = {
            'id': node_id,
            'location': locations_map.get(node_id, (0,0)), # Asume que locations_map se pasa
            'degree': self.degree(node_id),
            'in_degree': self.in_degree(node_id),
            'out_degree': self.out_degree(node_id),
            'neighbors': list(self.get_neighbors(node_id)),
        }
        return info

if __name__ == '__main__':
    # Ejemplo de uso básico
    cg = CustomGraph()
    cg.add_edge(1, 2)
    cg.add_edge(1, 3)
    cg.add_edge(2, 3)
    cg.add_edge(3, 1) # Ciclo

    print(f"Nodos: {cg.get_nodes()}")
    print(f"Aristas: {cg.get_edges()}")
    print(f"Número de nodos: {cg.number_of_nodes()}")
    print(f"Número de aristas: {cg.number_of_edges()}")

    print(f"Vecinos de 1: {cg.get_neighbors(1)}")
    print(f"Predecesores de 1: {cg.get_predecessors(1)}")
    print(f"Grado de 1: {cg.degree(1)}")
    print(f"Grado de entrada de 1: {cg.in_degree(1)}")
    print(f"Grado de salida de 1: {cg.out_degree(1)}")

    print(f"Vecinos de 4 (no existe): {cg.get_neighbors(4)}")

    # Grafo no dirigido
    ug = cg.to_undirected()
    print("\nGrafo no Dirigido:")
    print(f"Nodos: {ug.get_nodes()}")
    print(f"Aristas: {ug.get_edges()}")
    print(f"Vecinos de 1 (no dirigido): {ug.get_neighbors(1)}")
    print(f"Grado de 1 (no dirigido): {ug.degree(1)}")

    # Prueba de get_node_attributes
    locations = {1: (10.0, 20.0), 2: (11.0, 21.0), 3: (12.0, 22.0)}
    print(f"\nAtributos del nodo 1: {cg.get_node_attributes(1, locations)}")
