#!/usr/bin/env python3
"""
Aplicación Principal - Análisis de Red Social
Integra el código existente con una interfaz gráfica moderna
"""

import sys
import os
import logging
import platform
import subprocess

# Importaciones corregidas para ejecución directa desde 'python_app'
from gui_app import SocialNetworkApp as run_gui_class # Importa la clase directamente
from loader import load_location_data, load_user_data
from eda import run_location_eda, run_user_eda
import utils # Importa utils directamente

# Importar configuración
from config import LOCATION_FILE, USER_FILE, SAMPLE_SIZE

def setup_logging():
    """Configurar sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('social_network_analysis.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_data_files():
    """Verificar que los archivos de datos existan"""
    
    missing_files = []
    # Asegúrate de que los archivos estén en el mismo directorio que main.py
    # o ajusta la ruta si están en otro lugar (ej. un directorio 'data' en la raíz del proyecto)
    
    # Comprobar 10_million_location.txt
    location_path = os.path.join(os.path.dirname(__file__), '..', LOCATION_FILE)
    if not os.path.exists(location_path):
        missing_files.append(LOCATION_FILE)
    
    # Comprobar 10_million_user.txt
    user_path = os.path.join(os.path.dirname(__file__), '..', USER_FILE)
    if not os.path.exists(user_path):
        missing_files.append(USER_FILE)
    
    if missing_files:
        print("⚠️  ARCHIVOS FALTANTES:")
        for file in missing_files:
            print(f"   • {file}")
        print("\nPor favor, asegúrate de tener los archivos de datos en el directorio 'project' (uno arriba de 'python_app').")
        print("Los archivos deben llamarse:")
        print(f"   • {LOCATION_FILE}")
        print(f"   • {USER_FILE}")
        return False
    
    return True

def run_eda_analysis():
    """Ejecuta el análisis EDA."""
    logging.info("Iniciando análisis EDA...")
    print("Iniciando análisis EDA. Esto puede tomar un tiempo...")

    location_path = os.path.join(os.path.dirname(__file__), '..', LOCATION_FILE)
    user_path = os.path.join(os.path.dirname(__file__), '..', USER_FILE)

    location_df = load_location_data(location_path)
    user_df = load_user_data(user_path)

    if location_df is not None:
        run_location_eda(location_df)
    else:
        logging.error("No se pudieron cargar los datos de ubicación para el EDA.")
    
    if user_df is not None:
        run_user_eda(user_df)
    else:
        logging.error("No se pudieron cargar los datos de usuario para el EDA.")

    logging.info("Análisis EDA completado. Revisa los archivos de imagen generados (lat_hist.png, long_hist.png, degree_dist.png).")
    print("Análisis EDA completado. Revisa los archivos de imagen generados.")

    # Abrir la carpeta de trabajo donde se guardan las imágenes
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if platform.system() == "Windows":
        os.startfile(current_dir)
    elif platform.system() == "Darwin": # macOS
        subprocess.call(["open", current_dir])
    else: # Linux
        subprocess.call(["xdg-open", current_dir])

def run_gui():
    """Inicia la interfaz gráfica de usuario."""
    root = tk.Tk()
    # Pasa las rutas de los archivos directamente a la clase SocialNetworkApp
    # Asumiendo que los archivos están en el directorio 'project'
    location_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', LOCATION_FILE))
    user_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', USER_FILE))
    
    app = run_gui_class(root, location_file_path, user_file_path, SAMPLE_SIZE)
    root.mainloop()

if __name__ == "__main__":
    setup_logging()
    logging.info("Aplicación principal iniciada.")

    if not check_data_files():
        logging.error("Archivos de datos de entrada no encontrados. Por favor, corrígelos antes de continuar.")
        # Pausar la ejecución para que el usuario vea el mensaje
        input("\nPresiona Enter para continuar de todos modos (la aplicación podría fallar sin los datos)...")
    
    print("🚀 Iniciando aplicación de análisis de red social...")
    print()
    print("Funcionalidades disponibles:")
    print("   • 📁 Carga de datos de 10 millones de usuarios")
    print("   • 🗺️  Visualización en mapa mundial")
    print("   • 👥 Detección de comunidades (algoritmo Louvain)")
    print("   • 🛣️  Análisis de caminos más cortos")
    print("   • 📊 Estadísticas detalladas de la red")
    print("   • 🎨 Visualizaciones interactivas")
    print()
    
    try:
        # Preguntar si ejecutar EDA primero
        response = input("¿Deseas ejecutar el análisis EDA original primero? (s/N): ").lower()
        if response in ['s', 'si', 'sí', 'y', 'yes']:\
            run_eda_analysis()
        print()
        
        print("🖥️  Iniciando interfaz gráfica...")
        print("   • Usa los botones para cargar datos y realizar análisis")
        print("   • El mapa mostrará los nodos distribuidos globalmente")
        print("   • Puedes detectar comunidades y calcular caminos")
        print()
        
        # Iniciar aplicación GUI
        import tkinter as tk # Importa tkinter aquí para evitar problemas si EDA se ejecuta primero
        run_gui() # Llama a la función que inicia la GUI
        
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación cerrada por el usuario.")
    except Exception as e:
        logging.error(f"Error crítico: {e}")
        print(f"\n❌ Error crítico: {e}")
        print("Revisa el archivo de log para más detalles.")
    
    print("\n🔚 Aplicación finalizada.")