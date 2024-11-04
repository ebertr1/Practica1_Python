import json
from datetime import datetime
import os

def registrar_historial(operacion, entidad, detalle):
    # Definir la ruta del archivo JSON dentro de la carpeta `data`
    archivo_path = os.path.join("data", "historial.json")
    
    # Crear la carpeta `data` si no existe
    os.makedirs("data", exist_ok=True)

    # Estructura del registro
    registro = {
        "operacion": operacion,
        "entidad": entidad,
        "detalle": detalle,
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Intentar cargar el archivo JSON si existe, o inicializarlo como una lista vacía
    try:
        if os.path.exists(archivo_path):
            with open(archivo_path, "r") as archivo:
                historial = json.load(archivo)
                print("Historial cargado exitosamente.")
        else:
            print("Archivo de historial no encontrado, creando nuevo historial.")
            historial = []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error al leer el archivo JSON: {e}")
        historial = []

    # Agregar el nuevo registro al historial
    historial.append(registro)

    # Intentar guardar el historial actualizado en el archivo JSON
    try:
        with open(archivo_path, "w") as archivo:
            json.dump(historial, archivo, indent=4)
            print("Historial guardado exitosamente en data/historial.json.")
    except IOError as e:
        print(f"Error al guardar el archivo JSON: {e}")

