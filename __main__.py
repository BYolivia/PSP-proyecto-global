import sys
import os

# Agrega la ruta del directorio 'vista' al PYTHONPATH para asegurar que las importaciones funcionen
# Esto es una solución temporal para la ejecución directa si falla 'python -m proyecto'
# Lo más limpio es ejecutar con `python -m nombre_del_paquete` o configurar el IDE.
# Sin embargo, para la ejecución directa en el entorno de desarrollo, lo incluimos:
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vista.ventana_principal import VentanaPrincipal

if __name__ == "__main__":
    app = VentanaPrincipal()
    app.mainloop()
else:
    print("Cambia el nombre a __main__.py")