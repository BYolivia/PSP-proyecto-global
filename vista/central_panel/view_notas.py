# Módulo: vista/central_panel/view_notas.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# Asumo que la ruta de importación de la lógica es correcta
from logica.T1.textEditor import cargar_contenido_res_notes, guardar_contenido_res_notes
from vista.config import *


class NotasPanel(ttk.Frame):
    """
    Panel de la pestaña Tareas (Editor de Notas).
    """

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root
        self.notes_text_editor = None

        # 🎯 CORRECCIÓN CRÍTICA: Configurar la expansión del Frame de la pestaña
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.crear_interfaz_tareas(self)

    # -------------------------------------------------------------
    # 📄 VISTA Y LÓGICA DE NOTAS
    # -------------------------------------------------------------

    def crear_interfaz_tareas(self, parent_frame):
        """Crea el editor de texto simple para el archivo res/notes."""

        # 1. Frame Contenedor Principal. Lo ubicamos con grid para que ocupe todo el espacio.
        frame = ttk.Frame(parent_frame, padding=15, style='TFrame')
        # Usamos grid para ocupar el único espacio disponible en el parent_frame (NotasPanel)
        frame.grid(row=0, column=0, sticky="nsew")

        # 2. Configuración de expansión dentro del Frame Contenedor
        # Queremos que el Text widget sea el único que se expanda vertical y horizontalmente.
        # El Text widget está en la fila 2 (después de 2 labels).
        frame.grid_rowconfigure(2, weight=1)  # Fila del Text widget
        frame.grid_columnconfigure(0, weight=1)  # Columna única

        # Etiquetas (usan pack/grid si fuera necesario, pero aquí usaremos grid para simplificar)
        ttk.Label(frame, text="Editor de Notas ", font=FUENTE_TITULO).grid(row=0, column=0, pady=(0, 10), sticky="w")
        ttk.Label(frame, text="Use este panel para tomar notas rápidas sobre la ejecución de tareas.",
                  font=FUENTE_NEGOCIOS).grid(row=1, column=0, pady=(0, 15), sticky="w")

        # Editor de Texto
        self.notes_text_editor = tk.Text(
            frame,
            height=20,
            wrap="word",
            bg=COLOR_BLANCO,
            relief="solid",
            borderwidth=1,
            font=FUENTE_MONO
        )
        # 🎯 Ubicación del Text widget en la fila que tiene weight=1
        self.notes_text_editor.grid(row=2, column=0, sticky="nsew", pady=(0, 10))

        # Frame de Botones
        frame_botones = ttk.Frame(frame)
        frame_botones.grid(row=3, column=0, sticky="ew", pady=(5, 0))  # Colocado debajo del Text widget

        # Botones dentro del Frame de Botones (usando pack para alineación lateral)
        ttk.Button(frame_botones, text="Guardar Cambios", command=self.guardar_res_notes, style='Action.TButton').pack(
            side=tk.RIGHT)
        ttk.Button(frame_botones, text="Cargar Archivo", command=self.cargar_res_notes, style='Action.TButton').pack(
            side=tk.LEFT)

        self.cargar_res_notes(initial_load=True)

    def cargar_res_notes(self, initial_load=False):
        """Carga el contenido de res/notes al editor de texto."""
        if not self.notes_text_editor: return

        contenido = cargar_contenido_res_notes()
        self.notes_text_editor.delete("1.0", tk.END)

        if "Error al cargar:" in contenido:
            self.notes_text_editor.insert(tk.END, contenido)
        else:
            if initial_load and not contenido.strip():
                self.notes_text_editor.insert(tk.END, "# Escriba aquí sus notas (res/notes)")
            else:
                self.notes_text_editor.insert(tk.END, contenido)

    def guardar_res_notes(self):
        """Guarda el contenido del editor de texto en res/notes."""
        if not self.notes_text_editor: return

        contenido = self.notes_text_editor.get("1.0", tk.END)
        success, message = guardar_contenido_res_notes(contenido)

        if success:
            messagebox.showinfo("✅ Guardado", "Notas guardadas exitosamente.")
        else:
            messagebox.showerror("❌ Error al Guardar", message)