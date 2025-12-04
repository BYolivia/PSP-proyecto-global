import json
import os

# --- NOMBRE DEL ARCHIVO ---
NOMBRE_FICHERO = "radios.json"


def cargar_emisoras():
    """Carga las emisoras existentes desde el archivo, o retorna una lista vacía si no existe."""
    if os.path.exists(NOMBRE_FICHERO):
        try:
            with open(NOMBRE_FICHERO, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Error al leer el archivo {NOMBRE_FICHERO}. Creando una lista nueva.")
            return []
    return []


def guardar_emisoras(emisoras):
    """Guarda la lista de emisoras en formato JSON en el archivo."""
    try:
        with open(NOMBRE_FICHERO, 'w', encoding='utf-8') as f:
            # Usamos indent=4 para que el JSON sea legible
            json.dump(emisoras, f, indent=4, ensure_ascii=False)
        print(f"\n✅ ¡Éxito! El archivo '{NOMBRE_FICHERO}' ha sido guardado.")
    except Exception as e:
        print(f"\n❌ Error al intentar guardar el archivo: {e}")


def crear_nueva_emisora(emisoras):
    """Pide al usuario los datos de una nueva emisora y la añade a la lista."""
    print("\n--- Crear Nueva Emisora ---")

    # --- CAMPOS OBLIGATORIOS ---
    nombre = input("▶️ Nombre de la radio (ej: Jazz Clásico): ").strip()
    url = input("▶️ URL del Stream (ej: http://stream.com/live.mp3): ").strip()

    if not nombre or not url:
        print("❌ El nombre y la URL son obligatorios. Inténtalo de nuevo.")
        return

    # --- CAMPOS OPCIONALES ---
    pais = input("▶️ País (ej: ES, DE) [Opcional]: ").strip()
    genero = input("▶️ Género (ej: Pop, Noticias) [Opcional]: ").strip()

    nueva_emisora = {
        "nombre": nombre,
        "url_stream": url,
        "pais": pais if pais else None,
        "genero": genero if genero else None
    }

    emisoras.append(nueva_emisora)
    print(f"\n✅ Emisora '{nombre}' añadida a la lista en memoria.")


def mostrar_emisoras(emisoras):
    """Muestra la lista de emisoras actuales en memoria."""
    if not emisoras:
        print("\nLista de emisoras vacía. Utiliza la opción 1 para añadir una.")
        return

    print(f"\n--- Emisoras Actuales en Memoria ({len(emisoras)} en total) ---")
    for i, e in enumerate(emisoras):
        print(f"\nID: {i + 1}")
        print(f"  Nombre: {e.get('nombre', 'N/D')}")
        print(f"  URL: {e.get('url_stream', 'N/D')}")
        print(f"  País: {e.get('pais', 'N/D')}")
        print(f"  Género: {e.get('genero', 'N/D')}")
    print("--------------------------------------------------")


def menu_principal():
    """Función principal que ejecuta el menú interactivo."""

    # Cargar las emisoras al iniciar (si el archivo existe)
    emisoras_en_memoria = cargar_emisoras()

    while True:
        print("\n" + "=" * 30)
        print("📻 EDITOR DE CONFIGURACIÓN DE RADIOS 📻")
        print("=" * 30)
        print("1. Crear y Añadir Nueva Emisora")
        print("2. Mostrar Emisoras en Memoria")
        print(f"3. Guardar Lista en '{NOMBRE_FICHERO}'")
        print("4. Salir (Sin guardar los cambios en memoria)")
        print("-" * 30)

        opcion = input("Elige una opción (1-4): ").strip()

        if opcion == '1':
            crear_nueva_emisora(emisoras_en_memoria)
        elif opcion == '2':
            mostrar_emisoras(emisoras_en_memoria)
        elif opcion == '3':
            guardar_emisoras(emisoras_en_memoria)
        elif opcion == '4':
            print("\nSaliendo del editor. ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Por favor, selecciona un número del 1 al 4.")


if __name__ == "__main__":
    menu_principal()