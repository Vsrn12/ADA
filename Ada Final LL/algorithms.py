from collections import deque, defaultdict
import logging 
from custom_graph import CustomGraph 

# --- Algoritmos Básicos ---
def bfs_shortest_path(graph, start_node, end_node):
    if start_node == end_node:
        return [start_node]
    if start_node not in graph.get_nodes() or end_node not in graph.get_nodes():
        return None
    queue = deque([(start_node, [start_node])])
    visited = {start_node}
    while queue:
        current_node, path = queue.popleft()
        for neighbor in graph.get_neighbors(current_node):
            if neighbor == end_node:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None

def calculate_density(graph_undirected): # Asume grafo no dirigido para la fórmula común
    num_nodes = graph_undirected.number_of_nodes()
    # Para grafo no dirigido, m_unique = graph_undirected.number_of_edges() / 2
    # Densidad = 2 * m_unique / (N * (N-1)) = num_edges / (N * (N-1))
    num_edges_doubled = graph_undirected.number_of_edges() # Si to_undirected() duplica
    if num_nodes < 2: return 0.0
    max_possible_edges_doubled = num_nodes * (num_nodes - 1)
    if max_possible_edges_doubled == 0: return 0.0
    return num_edges_doubled / max_possible_edges_doubled

def get_connected_components(graph_undirected):
    if not graph_undirected.get_nodes(): return []
    visited = set()
    components = []
    for node in graph_undirected.get_nodes():
        if node not in visited:
            component = set()
            queue = deque([node])
            visited.add(node)
            component.add(node)
            while queue:
                curr = queue.popleft()
                for neighbor in graph_undirected.get_neighbors(curr):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        component.add(neighbor)
                        queue.append(neighbor)
            components.append(component)
    return components

def local_clustering_coefficient(graph_undirected, node_id):
    neighbors = graph_undirected.get_neighbors(node_id)
    degree = len(neighbors) # Grado no ponderado
    if degree < 2: return 0.0
    triangles = 0
    neighbor_list = list(neighbors)
    for i in range(len(neighbor_list)):
        for j in range(i + 1, len(neighbor_list)):
            if neighbor_list[j] in graph_undirected.get_neighbors(neighbor_list[i]):
                triangles += 1
    denominator = degree * (degree - 1)
    return (2 * triangles) / denominator if denominator > 0 else 0.0

def average_clustering_coefficient(graph_undirected):
    nodes = list(graph_undirected.get_nodes())
    if not nodes: return 0.0
    total_lcc = sum(local_clustering_coefficient(graph_undirected, node) for node in nodes)
    return total_lcc / len(nodes) if len(nodes) > 0 else 0.0

# --- Implementación de Louvain ---

def _calculate_modularity(graph_undirected, partition, m_formula):
    if m_formula == 0: return 0.0
    q = 0.0
    communities_props = defaultdict(lambda: {'sum_internal_weight': 0.0, 'sum_total_degree_weighted': 0.0})
    for node, comm_id in partition.items():
        communities_props[comm_id]['sum_total_degree_weighted'] += graph_undirected.degree(node, weighted=True)
    for u, v, weight in graph_undirected.get_edges(data=True):
        if partition[u] == partition[v]:
            communities_props[partition[u]]['sum_internal_weight'] += weight
    for comm_id, data in communities_props.items():
        sum_in_c = data['sum_internal_weight']
        sum_tot_c = data['sum_total_degree_weighted']
        term1 = sum_in_c / (2 * m_formula)
        term2 = (sum_tot_c / (2 * m_formula))**2
        q += (term1 - term2)
    return q

def _build_community_graph(original_graph_undirected, partition):
    aggregated_graph = CustomGraph()
    community_ids = set(partition.values())
    for comm_id in community_ids: aggregated_graph.add_node(comm_id)
    inter_community_edge_weights = defaultdict(float)
    for u, v, weight in original_graph_undirected.get_edges(data=True):
        if u >= v: continue # Procesar cada arista no dirigida única una vez
        comm_u, comm_v = partition[u], partition[v]
        if comm_u != comm_v:
            key = tuple(sorted((comm_u, comm_v)))
            inter_community_edge_weights[key] += weight
    for (c1, c2), total_weight in inter_community_edge_weights.items():
        if total_weight > 0:
            aggregated_graph.add_edge(c1, c2, weight=total_weight)
            aggregated_graph.add_edge(c2, c1, weight=total_weight)
    logging.info(f"_build_community_graph: Grafo agregado con {aggregated_graph.number_of_nodes()} nodos.")
    return aggregated_graph

def detect_communities_louvain(graph_input):
    if not graph_input or graph_input.number_of_nodes() == 0: return {}

    # `active_graph` es el grafo en el que se trabaja en el nivel actual (original o agregado)
    active_graph = graph_input.to_undirected() 
    
    # `node_to_overall_community` mapea nodos del grafo ORIGINAL a la ID de comunidad del nivel más alto actual
    node_to_overall_community = {node: node for node in graph_input.get_nodes()}
    
    overall_best_modularity = -float('inf')
    # `best_overall_partition_on_original` almacena la partición del grafo original que dio la mejor modularidad
    best_overall_partition_on_original = node_to_overall_community.copy()

    m_original_formula = sum(w for _,_,w in graph_input.to_undirected().get_edges(data=True)) / 2.0
    if m_original_formula == 0 and graph_input.number_of_nodes() > 0: # Grafo sin aristas
        return {node: i for i, node in enumerate(graph_input.get_nodes())}
    if m_original_formula == 0: return {}


    level = 0
    while True: # Bucle de niveles
        level += 1
        logging.info(f"Louvain: Iniciando Nivel {level}")
        num_nodes_active_graph = active_graph.number_of_nodes()
        if num_nodes_active_graph == 0: break

        # Partición para el nivel actual (nodos de `active_graph` a sub-comunidades)
        partition_this_level = {node: node for node in active_graph.get_nodes()}
        m2_this_level = sum(w for _,_,w in active_graph.get_edges(data=True)) # Esto es 2*m para el grafo actual
        if m2_this_level == 0: break 

        comm_total_degree_w = {node: active_graph.degree(node, weighted=True) for node in active_graph.get_nodes()}
        comm_internal_links_w = {node: 0.0 for node in active_graph.get_nodes()} # Σ_in para cada com (nodo individual)

        # Fase 1: Optimización de Modularidad Local
        moves_fase1 = 1
        passes_fase1 = 0
        while moves_fase1 > 0 and passes_fase1 < 30: # Límite de pasadas
            moves_fase1 = 0
            passes_fase1 += 1
            nodes_visit_fase1 = list(active_graph.get_nodes()) # Podría aleatorizarse

            for node_i in nodes_visit_fase1:
                orig_comm_i = partition_this_level[node_i]
                k_i_w = active_graph.degree(node_i, weighted=True)
                
                k_i_links_to_neigh_comms = defaultdict(float)
                for neighbor_j, weight_ij in active_graph.adj[node_i].items(): # adj da {vecino: peso}
                    k_i_links_to_neigh_comms[partition_this_level[neighbor_j]] += weight_ij
                k_i_to_original_comm_internal_w = k_i_links_to_neigh_comms.get(orig_comm_i, 0.0)
                
                best_target_comm = orig_comm_i
                max_dq = 0.0
                
                # Contribución de i a Q si se queda en su comunidad original
                # k_i_D_internal es k_i_links_to_neigh_comms[orig_comm_i]
                # Σ_tot_D_no_i = comm_total_degree_w[orig_comm_i] - k_i_w
                # gain_orig = (k_i_links_to_neigh_comms.get(orig_comm_i,0.0) / m2_this_level) - \
                #             ( (comm_total_degree_w[orig_comm_i] - k_i_w) * k_i_w / (m2_this_level**2) )
                
                for target_comm, k_i_to_target_comm_w in k_i_links_to_neigh_comms.items():
                    if target_comm == orig_comm_i: 
                        delta_q = 0.0 # Ganancia de "moverse" a la misma comunidad
                    else:
                        # ΔQ = [ (Σ_in_C + k_i_C) / 2m - ((Σ_tot_C + k_i)/2m)^2 ]_new - 
                        #      [ Σ_in_C_old / 2m - (Σ_tot_C_old/2m)^2 + Σ_in_D_old / 2m - (Σ_tot_D_old/2m)^2 ]_old
                        # Es más simple: ΔQ = (k_i_C / m) - (tot_deg_C * k_i / (2m^2))
                        # (para mover i a C, donde i no está en C, y C puede ser vacía)
                        # Esta es la ganancia al mover i a la comunidad C, respecto a i estando solo.
                        
                        # ΔQ = (k_i_C_w / m2) - ( (Σ_tot_C_w * k_i_w) / (m2^2) )
                        # Aquí, Σ_tot_C_w es la suma de grados de la comunidad C *antes* de que i se una.
                        # k_i_C_w es la suma de pesos de aristas de i a C.
                        
                        # Ganancia si i se mueve a target_comm
                        dq_target = k_i_to_target_comm_w - comm_total_degree_w[target_comm] * k_i_w / m2_this_level
                        
                        # Ganancia (negativa) si i se queda en orig_comm (enlaces internos de i)
                        dq_original = k_i_links_to_neigh_comms.get(orig_comm_i, 0.0) - \
                                      (comm_total_degree_w[orig_comm_i] - k_i_w) * k_i_w / m2_this_level
                                      
                        delta_q = dq_target - dq_original


                    if delta_q > max_dq:
                        max_dq = delta_q
                        best_target_comm = target_comm
                
                if best_target_comm != orig_comm_i and max_dq > 1e-7:
                    # Mover nodo y actualizar comm_total_degree_w y comm_internal_links_w
                    # (comm_internal_links_w no se usa directamente en el cálculo de ΔQ aquí, pero es para Q global)
                    
                    # Actualizar comm_total_degree_w
                    comm_total_degree_w[orig_comm_i] -= k_i_w
                    comm_total_degree_w[best_target_comm] += k_i_w
                    
                    # Actualizar comm_internal_links_w (Σ_in para cada comunidad)
                    # Cuando node_i se mueve de orig_comm_i a best_target_comm:
                    # - orig_comm_i pierde los enlaces internos que node_i tenía dentro de ella.
                    # - best_target_comm gana los enlaces que node_i ahora forma internamente con ella.
                    comm_internal_links_w[orig_comm_i] -= 2 * k_i_to_original_comm_internal_w # k_i_to_original_comm_internal_w fue calculado antes del bucle de target_comm
                    comm_internal_links_w[best_target_comm] += 2 * k_i_links_to_neigh_comms.get(best_target_comm, 0.0) # k_i_links_to_neigh_comms[best_target_comm] son los enlaces de i a la nueva comunidad
                    
                    partition_this_level[node_i] = best_target_comm
                    moves_fase1 += 1
            
            logging.debug(f"Louvain Nivel {level}, Fase 1, Pass {passes_fase1}: {moves_fase1} nodos movidos.") # Changed to debug
            if moves_fase1 == 0: break

        # Fase 1 completada para este nivel. Actualizar mapeo global.
        if level == 1:
            node_to_overall_community = partition_this_level.copy()
        else:
            # `active_graph_node_to_original_node_community` es `node_to_overall_community` del nivel anterior
            new_overall_community_map = {}
            for original_node, prev_level_comm_id in active_graph_node_to_original_node_community.items():
                new_overall_community_map[original_node] = partition_this_level[prev_level_comm_id]
            node_to_overall_community = new_overall_community_map
        
        current_global_modularity = _calculate_modularity(graph_input.to_undirected(), node_to_overall_community, m_original_formula)
        logging.info(f"Louvain Nivel {level}: Modularity global actual: {current_global_modularity:.6f}")

        if current_global_modularity - overall_best_modularity <= 1e-7 : # Tolerancia pequeña
            logging.info(f"Louvain: Convergencia global. Mejor modularity: {overall_best_modularity:.6f}")
            break 
        
        overall_best_modularity = current_global_modularity
        best_overall_partition_on_original = node_to_overall_community.copy()

        if moves_fase1 == 0 and level > 1: # Si la Fase 1 no movió nada en un grafo ya agregado
             logging.info("Louvain: Fase 1 no movió nodos en grafo agregado. Deteniendo.")
             break

        # Fase 2: Agregación
        logging.info(f"Louvain Nivel {level}: Iniciando Fase 2 (Agregación).")
        
        # Guardar el mapeo de nodos originales a las comunidades de este nivel (que serán los nodos del prox nivel)
        active_graph_node_to_original_node_community = node_to_overall_community.copy() 
        
        new_active_graph = _build_community_graph(active_graph, partition_this_level)
        
        if new_active_graph.number_of_nodes() == num_nodes_active_graph or new_active_graph.number_of_nodes() == 0:
             logging.info("Louvain: No más agregación posible o grafo vacío. Deteniendo.")
             break
        
        active_graph = new_active_graph
        # La partición para el nuevo `active_graph` (agregado) se reinicia para la siguiente Fase 1.
        # Las estructuras comm_total_degree_w y comm_internal_links_w se recalcularán.

    logging.info(f"Louvain finalizado. Mejor modularidad global: {overall_best_modularity:.6f}")
    return best_overall_partition_on_original

# --- Implementación de Kruskal y Union-Find ---

class UnionFind:
    """Estructura de datos Union-Find para el algoritmo de Kruskal."""
    def __init__(self, nodes):
        self.parent = {node: node for node in nodes}
        # self.rank = {node: 0 for node in nodes} # Usar tamaño para unión es otra opción
        self.num_nodes = {node: 1 for node in nodes}


    def find(self, node):
        """Encuentra el representante del conjunto del nodo con compresión de caminos."""
        if node not in self.parent: # Nodo nuevo añadido dinámicamente?
            self.parent[node] = node
            self.num_nodes[node] = 1
            return node
        if self.parent[node] == node:
            return node
        self.parent[node] = self.find(self.parent[node]) 
        return self.parent[node]

    def union(self, node1, node2):
        """Une los conjuntos de node1 y node2 usando unión por tamaño."""
        root1 = self.find(node1)
        root2 = self.find(node2)

        if root1 != root2:
            # Unir el árbol más pequeño al más grande
            if self.num_nodes[root1] < self.num_nodes[root2]:
                self.parent[root1] = root2
                self.num_nodes[root2] += self.num_nodes[root1]
            else:
                self.parent[root2] = root1
                self.num_nodes[root1] += self.num_nodes[root2]
            return True 
        return False 


def minimum_spanning_tree_kruskal(graph_undirected_weighted):
    """
    Encuentra un Árbol de Expansión Mínima (MST) o un Bosque de Expansión Mínima
    usando el algoritmo de Kruskal.
    Args:
        graph_undirected_weighted: Un CustomGraph no dirigido, potencialmente ponderado.
    Returns:
        Un nuevo CustomGraph representando el MST/MSF. Las aristas tendrán los pesos originales.
    """
    mst = CustomGraph()
    nodes = list(graph_undirected_weighted.get_nodes())
    if not nodes:
        return mst

    for node in nodes:
        mst.add_node(node)

    processed_edges = set() 
    sorted_edges_list = []
    # get_edges(data=True) devuelve (u,v,w). Como el grafo es no dirigido, u-v y v-u son la misma arista conceptual.
    # Necesitamos procesar cada arista conceptual única una sola vez.
    for u, v, weight in graph_undirected_weighted.get_edges(data=True):
        if u >= v: # Procesar cada par (u,v) una sola vez, asumiendo u < v
            continue
        sorted_edges_list.append({'u': u, 'v': v, 'weight': weight})
            
    sorted_edges_list.sort(key=lambda e: e['weight'])

    uf = UnionFind(nodes)
    num_edges_in_mst = 0
    
    for edge_data in sorted_edges_list:
        u, v, weight = edge_data['u'], edge_data['v'], edge_data['weight']

        if uf.find(u) != uf.find(v):
            mst.add_edge(u, v, weight=weight)
            mst.add_edge(v, u, weight=weight) 
            uf.union(u, v)
            num_edges_in_mst += 1
            
            # Para un grafo conectado, el MST tiene N-1 aristas.
            # Si el grafo no es conectado, esto producirá un bosque (MSF).
            # if num_edges_in_mst >= len(nodes) - 1: # Condición de parada para grafo conectado
            #     break 
    
    # El número de aristas en el mst será num_edges_in_mst * 2 porque añadimos u,v y v,u
    logging.info(f"Kruskal: MST/MSF construido con {mst.number_of_nodes()} nodos y {num_edges_in_mst} aristas únicas.")
    return mst
