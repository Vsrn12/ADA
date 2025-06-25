import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
# import matplotlib.pyplot as plt # Eliminado
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Eliminado
# from matplotlib.figure import Figure # Eliminado
import numpy as np
import threading
import logging
import folium # Añadido para Folium
from folium.plugins import MarkerCluster, FastMarkerCluster # Para agrupar marcadores
from tkhtmlview import HTMLLabel
import webbrowser # Para abrir HTML en navegador
import os # Para manejo de archivos
import tempfile # Para archivos HTML temporales

from graph_analyzer import GraphAnalyzer 
from loader import load_location_data, load_user_data 
import polars as pl

# Asegúrate de que estas importaciones relativas estén configuradas correctamente
# desde el punto de vista del paquete 'python_app' si gui_app.py está en 'python_app'
# Si gui_app.py está en la raíz, estas líneas pueden necesitar ser ajustadas.
# Asumo que la estructura es project/python_app/gui_app.py
from graph_analyzer import GraphAnalyzer
from config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, LOCATION_FILE, USER_FILE, MAX_NODES_DISPLAY, SAMPLE_SIZE
from loader import load_location_data, load_user_data # Importar las funciones de carga directamente

class SocialNetworkApp:
    def __init__(self, root, location_file_path, user_file_path, sample_size=None): # CAMBIO: Añade nuevos parámetros
        self.root = root
        self.location_file_path = location_file_path # CAMBIO: Guarda la ruta
        self.user_file_path = user_file_path         # CAMBIO: Guarda la ruta
        self.sample_size = sample_size               # CAMBIO: Guarda el tamaño de muestreo

        self.root.title(APP_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg='#2C3E50')
        
        # Inicializar analizador
        self.analyzer = GraphAnalyzer()
        self.current_path = []
        self.selected_nodes = []
        
        # Variables de estado
        self.data_loaded = False
        self.communities_detected = False
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior - Controles
        control_frame = tk.Frame(main_frame, bg='#34495E', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Botones de control
        btn_style = {'fg': '#EAECEE', 'bg': '#2874A6', 'font': ('Arial', 10, 'bold'), 'width': 18} # Increased width for better display
        
        self.load_button = tk.Button(control_frame, text="Cargar Datos", command=self.load_data_async, **btn_style)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.communities_button = tk.Button(control_frame, text="Detectar Comunidades", command=self.detect_communities_async, **btn_style)
        self.communities_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.communities_button.config(state=tk.DISABLED) # Deshabilitado al inicio

        # Entradas para camino más corto
        self.start_node_label = tk.Label(control_frame, text="Nodo Inicio:", bg='#34495E', fg='white')
        self.start_node_label.pack(side=tk.LEFT, padx=2)
        self.entry_start_node = tk.Entry(control_frame, width=10) 
        self.entry_start_node.pack(side=tk.LEFT, padx=2)
        self.entry_start_node.config(state=tk.DISABLED) # Deshabilitado al inicio

        self.end_node_label = tk.Label(control_frame, text="Nodo Fin:", bg='#34495E', fg='white')
        self.end_node_label.pack(side=tk.LEFT, padx=2)
        self.entry_end_node = tk.Entry(control_frame, width=10) 
        self.entry_end_node.pack(side=tk.LEFT, padx=2)
        self.entry_end_node.config(state=tk.DISABLED) # Deshabilitado al inicio
        
        self.find_path_button = tk.Button(control_frame, text="Camino Más Corto", command=self.find_path_async, **btn_style) 
        self.find_path_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.find_path_button.config(state=tk.DISABLED) # Deshabilitado al inicio

        self.clear_selection_button = tk.Button(control_frame, text="Limpiar Visualización", command=self.clear_visualization, **btn_style) 
        self.clear_selection_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.clear_selection_button.config(state=tk.DISABLED) # Deshabilitado al inicio

        self.stats_button = tk.Button(control_frame, text="Generar Estadísticas", command=self.generate_analysis_async, **btn_style)
        self.stats_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.stats_button.config(state=tk.DISABLED) # Deshabilitado al inicio

        self.mst_button = tk.Button(control_frame, text="Calcular MST", command=self.calculate_mst_async, **btn_style)
        self.mst_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.mst_button.config(state=tk.DISABLED) # Deshabilitado al inicio


        # Panel inferior - Contenedor para el gráfico y las estadísticas
        bottom_panel = tk.Frame(main_frame, bg='#2C3E50')
        bottom_panel.pack(fill=tk.BOTH, expand=True, pady=5)

        # Frame para el mapa (parte izquierda del bottom_panel)
        map_frame = tk.Frame(bottom_panel, bg='black') # Puedes ajustar el color de fondo si lo deseas
        map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configurar el widget para mostrar el mapa Folium (HTML)
        # Usaremos ScrolledHTMLText para poder ver mapas grandes si es necesario
        self.map_html_view = HTMLLabel(map_frame, html="<p>El mapa se mostrará aquí.</p>", background='#2C3E50')
        self.map_html_view.pack(fill=tk.BOTH, expand=True)
        self.map_html_view.fit_height() # Ajustar altura inicial

        # Panel lateral para estadísticas (parte derecha del bottom_panel)
        stats_frame = tk.Frame(bottom_panel, bg='#34495E', relief=tk.GROOVE, bd=2)
        stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5, ipadx=5) # Empaquetar a la derecha del bottom_panel

        stats_label = tk.Label(stats_frame, text="INFORMACIÓN DEL GRAFO", bg='#34495E', fg='#EAECEE', font=('Arial', 10, 'bold'))
        stats_label.pack(pady=5)

        self.stats_text = tk.Text(stats_frame, wrap=tk.WORD, bg='#476077', fg='white', font=('Consolas', 9),
                                 width=40, height=30, relief=tk.FLAT, padx=5, pady=5)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.stats_text.config(state=tk.DISABLED) # Hacerlo de solo lectura

        # No es necesario un botón de estadísticas aquí si ya lo tenemos en control_frame
        # self.generate_stats_button = tk.Button(stats_frame, text="Generar Estadísticas", command=self.generate_analysis_async, **btn_style)
        # self.generate_stats_button.pack(pady=5)


        # Etiqueta de estado
        self.status_label = tk.Label(self.root, text="Listo.", bg='#2C3E50', fg='white', font=('Arial', 9))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=2)

        # Matplotlib event handling para selección de nodos - ELIMINADO
        # self.scatter_nodes = None 
        # self.node_ids_scatter = [] 
        # self.fig.canvas.mpl_connect('pick_event', self.on_node_pick) # ELIMINADO


    def update_status(self, message, msg_type="info"):
        """Muestra mensajes en la etiqueta de estado y en el log."""
        logging.info(f"UI Message ({msg_type}): {message}")
        self.status_label.config(text=message)
        if msg_type == "error":
            self.status_label.config(fg='red')
        elif msg_type == "warning":
            self.status_label.config(fg='orange')
        else:
            self.status_label.config(fg='white')

    def load_data_async(self):
        """Cargar datos de forma asíncrona."""
        self.update_status("Cargando datos, por favor espere...", "info")
        self.load_button.config(state=tk.DISABLED)
        # Deshabilitar todos los botones interactivos mientras carga
        self.communities_button.config(state=tk.DISABLED)
        self.entry_start_node.config(state=tk.DISABLED)
        self.entry_end_node.config(state=tk.DISABLED)
        self.find_path_button.config(state=tk.DISABLED)
        self.clear_selection_button.config(state=tk.DISABLED)
        self.stats_button.config(state=tk.DISABLED)

        # Usar os.path.join para construir rutas robustas
        script_dir = os.path.dirname(__file__)
        location_filepath = os.path.join(script_dir, '..', LOCATION_FILE)
        user_filepath = os.path.join(script_dir, '..', USER_FILE)

        threading.Thread(target=self._load_data_task, args=(location_filepath, user_filepath)).start()

    def _load_data_task(self, location_file, user_file):
        """Tarea de carga de datos para ejecutar en un hilo separado."""
        try:
            # Cargar los DataFrames usando las funciones del módulo 'loader'
            location_df = load_location_data(self.location_file_path) # CAMBIO: Usa la ruta pasada
            user_df = load_user_data(self.user_file_path)           # CAMBIO: Usa la ruta pasada

            if location_df is None or user_df is None:
                raise ValueError("Error al cargar uno o ambos archivos de datos.")

            # Pasar los DataFrames al analizador de grafo
            self.analyzer.load_data(location_df, user_df, self.sample_size) # CAMBIO: Pasa el tamaño de muestreo
            print(f"DEBUG: Después de la carga, self.analyzer.locations tiene {len(self.analyzer.locations)} entradas.")

            self.data_loaded = True
            # Llamar al método de éxito en el hilo principal
            self.root.after(0, self._after_data_loaded_success)
        except Exception as e:
            logging.error(f"Error al cargar datos: {e}")
            self.data_loaded = False
            self.root.after(0, lambda: self.update_status(f"Error al cargar datos: {e}", "error"))
            self.root.after(0, lambda: self.load_button.config(state=tk.NORMAL)) # Re-habilitar botón de carga

    def _after_data_loaded_success(self):
        """Acciones a realizar después de que los datos se hayan cargado exitosamente."""
        self.update_status(f"Datos cargados exitosamente. Nodos: {self.analyzer.graph.number_of_nodes()}, Aristas: {self.analyzer.graph.number_of_edges()}", "info")
        self.load_button.config(state=tk.NORMAL) # Habilitar de nuevo por si se quiere cargar más datos

        # Habilitar los botones y campos relevantes
        self.communities_button.config(state=tk.NORMAL)
        self.entry_start_node.config(state=tk.NORMAL)
        self.entry_end_node.config(state=tk.NORMAL)
        self.find_path_button.config(state=tk.NORMAL)
        self.clear_selection_button.config(state=tk.NORMAL)
        self.stats_button.config(state=tk.NORMAL)
        self.mst_button.config(state=tk.NORMAL) # Habilitar botón MST
        
        self._render_folium_map_to_html_widget() # Dibujar el grafo inicial con Folium
        self.generate_analysis_async() # Generar estadísticas iniciales

    def _get_folium_map_center(self):
        """Calcula el centro para el mapa Folium basado en los nodos cargados."""
        if not self.data_loaded or not self.analyzer.locations:
            return [0, 0] # Centro global por defecto

        # Usar solo una muestra de ubicaciones para calcular el centro si hay muchas
        sample_locations = list(self.analyzer.locations.values())
        if len(sample_locations) > 1000:
            # Filtrar None o tuplas inválidas antes de np.random.choice
            valid_locations_for_sampling = [loc for loc in sample_locations if isinstance(loc, tuple) and len(loc) == 2]
            if not valid_locations_for_sampling: return [0,0]
            if len(valid_locations_for_sampling) < 1000 : # Si hay menos de 1000 válidas, usarlas todas
                 sample_locations = valid_locations_for_sampling
            else:
                indices = np.random.choice(len(valid_locations_for_sampling), 1000, replace=False)
                sample_locations = [valid_locations_for_sampling[i] for i in indices]


        if not sample_locations: # Si después del filtrado no queda nada
             return [0,0]

        # Filtrar otra vez por si acaso antes de mean
        lats = [loc[0] for loc in sample_locations if isinstance(loc, tuple) and len(loc) == 2 and loc[0] is not None]
        lngs = [loc[1] for loc in sample_locations if isinstance(loc, tuple) and len(loc) == 2 and loc[1] is not None]

        if not lats or not lngs: return [0,0]

        avg_lat = np.mean(lats)
        avg_lng = np.mean(lngs)
        
        if np.isnan(avg_lat) or np.isnan(avg_lng): 
            return [0,0]
            
        return [avg_lat, avg_lng]

    def _render_folium_map_to_html_widget(self, path_nodes=None, highlight_communities=None, mst_graph=None):
        """
        Crea un mapa Folium y lo renderiza en el widget ScrolledHTMLText.
        path_nodes: una lista de nodos para resaltar como un camino.
        highlight_communities: un dict de comunidades {comm_id: data} para colorear nodos.
        mst_graph: un CustomGraph que representa el MST.
        """
        if not self.data_loaded:
            self.map_html_view.set_html("<p>Cargue datos para ver el mapa.</p>")
            return

        map_center = self._get_folium_map_center()
        # Usar tiles de OpenStreetMap por defecto, o CartoDB positron para un look más limpio
        folium_map = folium.Map(location=map_center, zoom_start=2, tiles="CartoDB positron")

        node_positions = {
            node_id: loc for node_id, loc in self.analyzer.locations.items() 
            if node_id in self.analyzer.graph.get_nodes() # Solo nodos que están en el grafo
        }

        # Limitar nodos para visualización
        nodes_to_display_ids = list(node_positions.keys())
        if MAX_NODES_DISPLAY and len(nodes_to_display_ids) > MAX_NODES_DISPLAY:
            nodes_to_display_ids = np.random.choice(nodes_to_display_ids, MAX_NODES_DISPLAY, replace=False)
        
        # Crear un FeatureGroup para los marcadores para poder usar MarkerCluster
        marker_group = folium.FeatureGroup(name="Nodos")
        # Para mejor rendimiento con muchos marcadores, usar FastMarkerCluster
        # fast_marker_cluster = FastMarkerCluster(data=[], name="Nodos Agrupados").add_to(folium_map)


        # Colores para comunidades (simplificado, se puede mejorar)
        community_colors = {}
        if highlight_communities and self.communities_detected:
            unique_comm_ids = sorted(list(highlight_communities.keys()))
            # Usar un conjunto simple de colores o generar más si es necesario
            available_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                                'lightblue', 'darkgreen', 'cadetblue', 'pink', 'lightgray', 'black']
            for i, comm_id in enumerate(unique_comm_ids):
                community_colors[comm_id] = available_colors[i % len(available_colors)]

        for node_id in nodes_to_display_ids:
            if node_id in node_positions:
                lat, lng = node_positions[node_id]
                
                # Determinar color y pop-up
                color = 'blue' # Color por defecto
                popup_text = f"Nodo ID: {node_id}<br>Lat: {lat:.8f}, Lng: {lng:.8f}"

                if highlight_communities and self.communities_detected:
                    for comm_id, comm_data in highlight_communities.items():
                        if node_id in comm_data['nodes']:
                            color = community_colors.get(comm_id, 'gray')
                            popup_text += f"<br>Comunidad: {comm_id}"
                            break
                
                if path_nodes and node_id in path_nodes:
                    color = 'lime' # Nodos en el camino resaltados
                    # Podríamos usar un icono diferente o radio más grande para nodos del camino
                    folium.CircleMarker(
                        location=[lat, lng],
                        radius=8,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.8,
                        popup=folium.Popup(popup_text, max_width=200)
                    ).add_to(marker_group)
                else:
                    folium.CircleMarker(
                        location=[lat, lng],
                        radius=3, # Radio más pequeño para nodos normales
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.6,
                        popup=folium.Popup(popup_text, max_width=200)
                    ).add_to(marker_group)
        
        marker_group.add_to(folium_map)
        # fast_marker_cluster.add_to(folium_map) # Si se usa FastMarkerCluster

        # Dibujar camino más corto
        if path_nodes and len(path_nodes) > 1:
            path_coords = []
            for node_id in path_nodes:
                if node_id in node_positions:
                    path_coords.append(node_positions[node_id])
            if path_coords:
                folium.PolyLine(path_coords, color="red", weight=2.5, opacity=1).add_to(folium_map)
        
        # Dibujar aristas del MST
        if mst_graph:
            mst_edges_group = folium.FeatureGroup(name="MST Edges")
            for u, v in mst_graph.get_edges(): # Asumiendo que get_edges() devuelve las aristas del MST
                if u in node_positions and v in node_positions:
                    start_pos = node_positions[u]
                    end_pos = node_positions[v]
                    # Dibujar solo una dirección para evitar duplicados visuales si to_undirected duplicó
                    if u < v: # Simple heurística para dibujar cada arista no dirigida una vez
                        folium.PolyLine([start_pos, end_pos], color="cyan", weight=1.5, opacity=0.7).add_to(mst_edges_group)
            mst_edges_group.add_to(folium_map)
            folium.LayerControl().add_to(folium_map) # Añadir control de capas si tenemos MST

        # Guardar en un archivo HTML temporal
        temp_html_file = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmpfile:
                folium_map.save(tmpfile.name)
                temp_html_file = tmpfile.name
                print(f"DEBUG: Mapa temporal guardado en: {temp_html_file}")
                import webbrowser
                webbrowser.open(f"file://{temp_html_file}")

            with open(temp_html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            self.map_html_view.set_html(html_content)
            
        except Exception as e:
            logging.error(f"Error al renderizar mapa Folium: {e}")
            self.map_html_view.set_html(f"<p>Error al generar el mapa: {e}</p>")
        #finally:
        #    if temp_html_file and os.path.exists(temp_html_file):
        #        try:
        #            os.remove(temp_html_file)
        #        except OSError as e:
        #            logging.warning(f"No se pudo eliminar el archivo temporal del mapa: {e}")


    def _update_map_visualization(self):
        """Actualiza la visualización del mapa Folium."""
        path_to_draw = self.current_path if self.current_path else None
        communities_to_draw = self.analyzer.communities if self.communities_detected else None
        mst_to_draw = self.analyzer.mst # Obtener el MST calculado desde el analizador
        self._render_folium_map_to_html_widget(
            path_nodes=path_to_draw, 
            highlight_communities=communities_to_draw,
            mst_graph=mst_to_draw
        )

    def detect_communities_async(self):
        """Detectar comunidades de forma asíncrona."""
        if not self.data_loaded:
            self.update_status("Por favor, cargue los datos primero.", "warning")
            return
        
        self.update_status("Detectando comunidades, esto puede tardar...", "info")
        self.communities_button.config(state=tk.DISABLED)
        threading.Thread(target=self._detect_communities_task).start()

    def _detect_communities_task(self):
        """Tarea de detección de comunidades para ejecutar en un hilo separado."""
        try:
            self.analyzer.detect_communities()
            self.communities_detected = True
            self.root.after(0, self._after_communities_detected_success)
        except Exception as e:
            logging.error(f"Error al detectar comunidades: {e}")
            self.communities_detected = False
            self.root.after(0, lambda: self.update_status(f"Error al detectar comunidades: {e}", "error"))
            self.root.after(0, lambda: self.communities_button.config(state=tk.NORMAL))

    def _after_communities_detected_success(self):
        """Acciones a realizar después de que las comunidades se hayan detectado exitosamente."""
        self.update_status(f"Comunidades detectadas: {len(self.analyzer.communities)}", "info")
        self.communities_button.config(state=tk.NORMAL)
        self._update_map_visualization()
        self.generate_analysis_async() # Actualizar estadísticas para incluir las comunidades

    def find_path_async(self):
        """Encontrar el camino más corto de forma asíncrona."""
        if not self.data_loaded:
            self.update_status("Por favor, cargue los datos primero.", "warning")
            return

        try:
            start_node = int(self.entry_start_node.get())
            end_node = int(self.entry_end_node.get())
        except ValueError:
            self.update_status("Por favor, ingrese IDs de nodo válidos.", "warning")
            return
        
        # Comprobar si los nodos existen usando get_nodes() de CustomGraph
        current_graph_nodes = self.analyzer.graph.get_nodes()
        if start_node not in current_graph_nodes or end_node not in current_graph_nodes:
            self.update_status("Uno o ambos nodos no existen en el grafo.", "warning")
            return

        self.update_status(f"Buscando camino de {start_node} a {end_node}...", "info")
        self.find_path_button.config(state=tk.DISABLED)
        threading.Thread(target=self._find_path_task, args=(start_node, end_node)).start()

    def _find_path_task(self, start_node, end_node):
        """Tarea de búsqueda de camino para ejecutar en un hilo separado."""
        try:
            path = self.analyzer.find_shortest_path(start_node, end_node)
            self.root.after(0, lambda: self._after_find_path_success(path, start_node, end_node))
        except Exception as e:
            logging.error(f"Error al encontrar el camino: {e}")
            self.root.after(0, lambda: self.update_status(f"Error al encontrar el camino: {e}", "error"))
            self.root.after(0, lambda: self.find_path_button.config(state=tk.NORMAL))

    def _after_find_path_success(self, path, start_node, end_node):
        """Acciones a realizar después de que el camino se haya encontrado exitosamente."""
        if path:
            self.current_path = path
            self.update_status(f"Camino encontrado: {len(path)-1} aristas. Distancia: {self.analyzer.get_path_distance(path):.2f}", "info")
        else:
            self.current_path = []
            self.update_status(f"No se encontró camino entre {start_node} y {end_node}.", "warning")
        
        self.find_path_button.config(state=tk.NORMAL)
        self._update_map_visualization()

    def generate_analysis_async(self):
        """Generar análisis y estadísticas de forma asíncrona."""
        if not self.data_loaded:
            self.update_status("Por favor, cargue los datos primero para generar estadísticas.", "warning")
            return
        
        self.update_status("Generando estadísticas, por favor espere...", "info")
        self.stats_button.config(state=tk.DISABLED)
        threading.Thread(target=self._generate_analysis_task).start()

    def _generate_analysis_task(self):
        """Tarea de generación de análisis para ejecutar en un hilo separado."""
        try:
            # Aquí puedes llamar a métodos del analizador que realicen cálculos pesados
            # Luego, el resultado se pasa al hilo principal para actualizar la UI
            self.root.after(0, self._update_stats_display_from_analysis)
        except Exception as e:
            logging.error(f"Error al generar análisis: {e}")
            self.root.after(0, lambda: self.update_status(f"Error al generar análisis: {e}", "error"))
            self.root.after(0, lambda: self.stats_button.config(state=tk.NORMAL))

    def _update_stats_display_from_analysis(self):
        """Actualiza el widget de texto de estadísticas con los resultados del análisis."""
        text_widget = self.stats_text
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)

        detailed_stats = "ESTADÍSTICAS DEL GRAFO:\n"
        detailed_stats += f"• Nodos totales: {self.analyzer.graph.number_of_nodes():,}\n"
        detailed_stats += f"• Aristas totales: {self.analyzer.graph.number_of_edges():,}\n"
        
        # Calcular densidad y otros solo si hay nodos
        if self.analyzer.graph.number_of_nodes() > 0:
            density = self.analyzer.get_density()
            detailed_stats += f"• Densidad de la red: {density:.6f}\n"

            # Componentes conectados (solo para grafos no dirigidos)
            num_components = self.analyzer.get_number_connected_components()
            detailed_stats += f"• Componentes conectados: {num_components}\n"
            if num_components > 1 and self.analyzer.graph.number_of_nodes() > 0 : # Asegurar que haya nodos antes de pedir el más grande
                largest_cc_size = self.analyzer.get_largest_connected_component_size()
                detailed_stats += f"• Tamaño del componente más grande: {largest_cc_size:,}\n"
            
            # Coeficiente de clustering promedio (solo para grafos no dirigidos)
            avg_clustering = self.analyzer.get_average_clustering_coefficient()
            detailed_stats += f"• Coeficiente de clustering promedio: {avg_clustering:.4f}\n"
            
            # Grado promedio
            num_nodes = self.analyzer.graph.number_of_nodes()
            if num_nodes > 0:
                total_degree = 0
                for node in self.analyzer.graph.get_nodes():
                    total_degree += self.analyzer.graph.degree(node) # Usando CustomGraph.degree()
                avg_degree = total_degree / num_nodes
                detailed_stats += f"• Grado promedio: {avg_degree:.2f}\n"
            else:
                detailed_stats += f"• Grado promedio: N/A\n"
        else:
            detailed_stats += "No hay nodos para calcular métricas avanzadas.\n"

        geo_stats = self.analyzer.analyze_geographic_distribution()
        if geo_stats:
            detailed_stats += "\nANÁLISIS GEOGRÁFICO:\n"
            detailed_stats += f"• Rango de latitud: {geo_stats.get('lat_range', (0,0))[0]:.4f} a {geo_stats.get('lat_range', (0,0))[1]:.4f}\n"
            detailed_stats += f"• Rango de longitud: {geo_stats.get('lng_range', (0,0))[0]:.4f} a {geo_stats.get('lng_range', (0,0))[1]:.4f}\n"
            detailed_stats += f"• Centro geográfico: ({geo_stats.get('lat_center', 0):.4f}, {geo_stats.get('lng_center', 0):.4f})\n\n"
        
        if self.communities_detected and self.analyzer.communities:
            detailed_stats += "ANÁLISIS DE COMUNIDADES:\n"
            detailed_stats += f"• Total de comunidades: {len(self.analyzer.communities)}\n"
            # Mostrar solo las 5 comunidades más grandes para no saturar
            sorted_communities = sorted(self.analyzer.communities.items(), key=lambda item: item[1]['size'], reverse=True)
            for i, (comm_id, comm_data) in enumerate(sorted_communities[:5]):
                detailed_stats += f"• Comunidad {comm_id}: {comm_data['size']} nodos\n"
                detailed_stats += f"  Centro: ({comm_data['center_lat']:.2f}, {comm_data['center_lng']:.2f})\n"
            if len(sorted_communities) > 5:
                detailed_stats += f"  ... y {len(sorted_communities) - 5} comunidades más.\n"
            detailed_stats += "\n"
        elif self.data_loaded:
             detailed_stats += "\nANÁLISIS DE COMUNIDADES:\n"
             detailed_stats += "• Comunidades aún no detectadas.\n\n"
        
        # Top nodos conectados
        top_nodes = self.analyzer.get_top_connected_nodes(10)
        if top_nodes:
            detailed_stats += "NODOS MÁS CONECTADOS (TOP 10 por grado):\n"
            for i, (node, degree) in enumerate(top_nodes, 1):
                detailed_stats += f"{i:2d}. Nodo {node:8d}: {degree:4d} conexiones\n"
        else:
            detailed_stats += "No hay nodos conectados para mostrar.\n"

        text_widget.insert(tk.END, detailed_stats)
        text_widget.config(state=tk.DISABLED)
        self.stats_button.config(state=tk.NORMAL) # Re-habilitar botón de estadísticas


    def on_click_node(self, event):
        """Manejador general para clics en el lienzo del mapa (no necesariamente en un nodo)."""
        # Esta función puede ser útil para deseleccionar nodos al hacer clic en el vacío del mapa
        # o para mostrar coordenadas del clic si no se seleccionó un nodo.

        # Verificar si un nodo fue seleccionado por on_node_pick.
        # Si on_node_pick maneja la lógica de selección/deselección de nodos,
        # este método puede usarse para deseleccionar si el clic no fue en un nodo.
        # Por ahora, simplemente limpia la selección si no se ha hecho clic en un nodo disperso
        # y no hay un nodo ya seleccionado para camino.
        if self.selected_nodes and not self.entry_start_node.get() and not self.entry_end_node.get():
            self.clear_selection() # Deselecciona si no estamos en proceso de elegir camino
        
        # Puedes añadir más lógica aquí, como mostrar coordenadas del clic
        # logging.info(f"Clic en el mapa: x={event.x}, y={event.y}")

    def on_node_pick(self, event):
        """Manejador de eventos para seleccionar nodos en el scatter plot."""
        if event.artist == self.scatter_nodes:
            ind = event.ind[0] # Índice del nodo clickeado
            node_id = self.node_ids_scatter[ind] # Obtener el ID de nodo real

            if node_id not in self.selected_nodes:
                self.selected_nodes.append(node_id)
                self.update_status(f"Nodo seleccionado: {node_id}")
            else:
                self.selected_nodes.remove(node_id)
                self.update_status(f"Nodo deseleccionado: {node_id}")

            # Limitar a 2 nodos para el camino más corto
            if len(self.selected_nodes) > 2:
                self.selected_nodes = self.selected_nodes[-2:] # Mantener solo los dos últimos

            # Actualizar campos de entrada
            if len(self.selected_nodes) >= 1:
                self.entry_start_node.config(state=tk.NORMAL)
                self.entry_start_node.delete(0, tk.END)
                self.entry_start_node.insert(0, str(self.selected_nodes[0]))
            else:
                self.entry_start_node.config(state=tk.NORMAL) # keep enabled but empty
                self.entry_start_node.delete(0, tk.END)

            if len(self.selected_nodes) == 2:
                self.entry_end_node.config(state=tk.NORMAL)
                self.entry_end_node.delete(0, tk.END)
                self.entry_end_node.insert(0, str(self.selected_nodes[1]))
            else:
                self.entry_end_node.config(state=tk.NORMAL) # keep enabled but empty
                self.entry_end_node.delete(0, tk.END)

            self._update_map_visualization() # Redibujar para mostrar la selección

    def clear_selection(self):
        """Limpia la selección actual de nodos y la visualización del camino."""
        self.selected_nodes = []
        self.current_path = []
        self.entry_start_node.delete(0, tk.END)
        self.entry_end_node.delete(0, tk.END)
        self.update_status("Selección y camino limpiados.", "info")
        self._update_map_visualization()

    def clear_visualization(self):
        """Limpia toda la visualización del grafo y reinicia el estado."""
        # Limpiar el widget de Folium
        self.map_html_view.set_html("<p>Mapa limpiado. Cargue nuevos datos.</p>")

        self.selected_nodes = [] # Aunque la selección directa en mapa no está, mantenemos por si se usa para entradas de camino
        self.current_path = []
        self.data_loaded = False
        self.communities_detected = False
        
        self.entry_start_node.delete(0, tk.END)
        self.entry_end_node.delete(0, tk.END)

        # Deshabilitar todos los botones excepto Cargar Datos
        self.communities_button.config(state=tk.DISABLED)
        self.entry_start_node.config(state=tk.DISABLED)
        self.entry_end_node.config(state=tk.DISABLED)
        self.find_path_button.config(state=tk.DISABLED)
        self.clear_selection_button.config(state=tk.DISABLED)
        self.stats_button.config(state=tk.DISABLED)

        self.update_status("Visualización limpiada y estado reiniciado. Carga nuevos datos.", "info")
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "No hay datos cargados para mostrar estadísticas.")
        self.stats_text.config(state=tk.DISABLED)

    def calculate_mst_async(self):
        """Calcula el MST de forma asíncrona."""
        if not self.data_loaded:
            self.update_status("Por favor, cargue los datos primero para calcular el MST.", "warning")
            return

        self.update_status("Calculando Árbol de Expansión Mínima (MST)...", "info")
        self.mst_button.config(state=tk.DISABLED)
        self.find_path_button.config(state=tk.DISABLED) # Deshabilitar otros botones de análisis
        self.communities_button.config(state=tk.DISABLED)

        threading.Thread(target=self._calculate_mst_task).start()

    def _calculate_mst_task(self):
        """Tarea de cálculo de MST para ejecutar en un hilo separado."""
        try:
            self.analyzer.calculate_minimum_spanning_tree() # Llama al método en GraphAnalyzer
            # El resultado se guarda en self.analyzer.mst
            self.root.after(0, self._after_mst_calculated_success)
        except Exception as e:
            logging.error(f"Error al calcular MST: {e}")
            self.root.after(0, lambda: self.update_status(f"Error al calcular MST: {e}", "error"))
        finally:
            # Volver a habilitar botones en el hilo principal
            self.root.after(0, lambda: self.mst_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.find_path_button.config(state=tk.NORMAL if self.data_loaded else tk.DISABLED))
            self.root.after(0, lambda: self.communities_button.config(state=tk.NORMAL if self.data_loaded else tk.DISABLED))


    def _after_mst_calculated_success(self):
        """Acciones a realizar después de que el MST se haya calculado exitosamente."""
        if self.analyzer.mst and self.analyzer.mst.number_of_edges() > 0:
            num_edges = self.analyzer.mst.number_of_edges()
            self.update_status(f"MST calculado con {num_edges} aristas.", "info")
        elif self.analyzer.mst: # Existe pero está vacío
             self.update_status("MST calculado, pero resultó en un grafo vacío (0 aristas).", "info")
        else: # No se pudo calcular o no se inicializó
            self.update_status("Cálculo de MST no produjo resultados.", "warning")
        
        self._update_map_visualization() # Redibujar el mapa para mostrar el MST


# Funciones on_click_node y on_node_pick eliminadas ya que eran específicas de Matplotlib.
# La interacción con el mapa Folium se manejará de forma diferente (pop-ups, etc.)

def main():
    """Función principal para ejecutar la aplicación Tkinter."""
    # Esto es para prueba, la app se inicia desde main.py del proyecto.
    # Para ejecutar gui_app.py directamente para testear UI:
    # root = tk.Tk()
    # # Necesitarías pasar paths dummy o configurar para pruebas
    # # location_path_dummy = "dummy_locations.txt" 
    # # user_path_dummy = "dummy_users.txt"
    # # with open(location_path_dummy, "w") as f: f.write("0,0\n1,1\n")
    # # with open(user_path_dummy, "w") as f: f.write("1\n0\n")
    # # app = SocialNetworkApp(root, location_path_dummy, user_path_dummy, sample_size=2)
    # # root.mainloop()
    # # os.remove(location_path_dummy)
    # # os.remove(user_path_dummy)
    print("gui_app.py no está pensado para ser ejecutado directamente sin main.py, a menos que se configure para pruebas.")


if __name__ == "__main__":
    # main() # Comentado para evitar ejecución directa accidental sin contexto
    pass