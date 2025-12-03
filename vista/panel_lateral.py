# Módulo: vista/panel_lateral.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from logica.controlador import accion_placeholder
from logica.T1.backup import accion_backup_t1
from logica.T1.runVScode import abrir_vscode
from logica.T1.textEditor import cargar_contenido_res_notes, guardar_contenido_res_notes
from logica.T1.openBrowser import navegar_a_url



class PanelLateral(ttk.Frame):
    """Contiene el menú de botones, entradas para las tareas y el editor simple para res/notes."""

    # Definimos un ancho fijo en caracteres. Esto es crucial para que Tkinter
    # no intente expandir el panel lateral más allá de lo deseado.
    ANCHO_CARACTERES_FIJO = 35

    ANCHO_CARACTERES_FIJO = 35

    def __init__(self, parent, central_panel=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.central_panel = central_panel

        self.configurar_estilos_locales(parent)

        # 1. Entrada superior (amarilla) - ¡Guardamos la referencia!
        self.entrada_superior = ttk.Entry(self, width=self.ANCHO_CARACTERES_FIJO, style='Yellow.TEntry')
        self.entrada_superior.pack(fill="x", pady=10, padx=5, ipady=3)
        self.entrada_superior.bind('<Return>', self.manejar_navegacion)  # Opcional: Ejecutar con Enter

        # 2. Área de Extracción/Navegación
        acciones_extraccion = [
            ("Extraer datos", self.manejar_extraccion_datos),
            # 2. Asignamos el nuevo método de manejo a este botón
            ("Navegar", self.manejar_navegacion),
            ("Buscar API Google", lambda: accion_placeholder("Buscar API Google"))
        ]
        self.crear_seccion(self, titulo="", acciones=acciones_extraccion)

        # 3. Área de Aplicaciones
        acciones_aplicaciones = [
            ("Visual Code", abrir_vscode),
            ("App2", lambda: accion_placeholder("App2")),
            ("App3", lambda: accion_placeholder("App3"))
        ]
        self.crear_seccion(self, titulo="Aplicaciones", acciones=acciones_aplicaciones)

        # 4. Área de Procesos Batch
        acciones_batch = [
            ("Copias de seguridad", self.manejar_backup)
        ]
        self.crear_seccion(self, titulo="Procesos batch", acciones=acciones_batch)

        # 5. Espacio expandible
        tk.Frame(self, height=1).pack(expand=True, fill="both")

        # 6. Panel de Notas
        self.crear_editor_res_notes()

    # --- NUEVO MÉTODO PARA MANEJAR LA NAVEGACIÓN ---
    def manejar_navegacion(self, event=None):
        """
        Obtiene el texto de la entrada superior y llama a la función de navegación.
        """
        url = self.entrada_superior.get()
        if navegar_a_url(url):
            # Limpiar la casilla si la navegación fue exitosa
            self.entrada_superior.delete(0, tk.END)
    # --- LÓGICA DEL EDITOR res/notes ---

    def crear_editor_res_notes(self):
        """Crea el editor de texto simple para el archivo res/notes."""

        ttk.Label(self, text="Editor Simple (res/notes)", font=('Arial', 11, 'bold')).pack(fill="x", pady=(10, 0),
                    padx=5)

        frame_editor = ttk.Frame(self, padding=5)
        frame_editor.pack(fill="x", padx=5, pady=(0, 10))

        # 1. Widget de texto - Aplicamos el ancho fijo
        self.notes_text_editor = tk.Text(
            frame_editor,
            height=8,
            width=self.ANCHO_CARACTERES_FIJO,
            wrap="word",
            bg='white',
            relief="solid",
            borderwidth=1,
            font=('Consolas', 9)  # Fuente tipo terminal
        )
        self.notes_text_editor.pack(fill="x", expand=False)

        # 2. Botones de Cargar y Guardar
        frame_botones = ttk.Frame(frame_editor)
        frame_botones.pack(fill="x", pady=(5, 0))

        # Se usa 'SmallAction.TButton' para reducir el padding y asegurar que quepan
        ttk.Button(frame_botones, text="Guardar", command=self.guardar_res_notes, style='SmallAction.TButton').pack(
            side=tk.RIGHT)
        ttk.Button(frame_botones, text="Cargar", command=self.cargar_res_notes, style='SmallAction.TButton').pack(
            side=tk.LEFT)

        self.cargar_res_notes(initial_load=True)  # Carga inicial

    def cargar_res_notes(self, initial_load=False):
        """Carga el contenido de res/notes al editor de texto lateral."""
        contenido = cargar_contenido_res_notes()

        self.notes_text_editor.delete("1.0", tk.END)  # Limpiar contenido actual

        if "Error al cargar:" in contenido:
            self.notes_text_editor.insert(tk.END, contenido)
        else:
            if initial_load and not contenido.strip():
                self.notes_text_editor.insert(tk.END, "# Escriba aquí sus notas (res/notes)")
            else:
                self.notes_text_editor.insert(tk.END, contenido)

        print("Cargado 'res/notes' en el editor lateral.")

    def guardar_res_notes(self):
        """Guarda el contenido del editor de texto lateral en res/notes."""
        # CORRECCIÓN: Quitamos .strip() para que el guardado refleje fielmente el contenido
        # del widget, incluyendo saltos de línea finales, lo que soluciona la confusión
        # de que "se guarda, pero el archivo está vacío".
        contenido = self.notes_text_editor.get("1.0", tk.END)

        success, message = guardar_contenido_res_notes(contenido)

        if success:
            messagebox.showinfo("✅ Guardado", "Notas guardadas exitosamente.")
            print(message)
        else:
            messagebox.showerror("❌ Error al Guardar", message)
            print(f"FALLO AL GUARDAR: {message}")

    # --- MÉTODOS EXISTENTES ---
    def manejar_extraccion_datos(self):
        """
        Llama a la lógica de actualización del gráfico de recursos
        en el panel central (actualización manual).
        """
        if self.central_panel:
            print("Activando actualización del gráfico de Recursos (Manual)...")
            self.central_panel.actualizar_grafico_recursos()
        else:
            messagebox.showerror("Error", "El Panel Central no está inicializado.")

    def manejar_backup(self):
        """Llama a la lógica de backup de T1 e informa al usuario del resultado."""
        print("Iniciando proceso de Copia de Seguridad...")
        success, message = accion_backup_t1()

        if success:
            messagebox.showinfo("✅ Backup Completado", message)
        else:
            messagebox.showerror("❌ Error en el Backup", message)

    def configurar_estilos_locales(self, parent):
        """Configura estilos para los widgets del panel lateral."""
        style = ttk.Style(parent)

        # Estilos existentes
        style.configure('Yellow.TEntry', fieldbackground='#fff8e1', foreground='#333333', padding=[5, 5],
                        relief='solid', borderwidth=1)
        style.configure('Green.TButton', background='#4CAF50', foreground='white', font=('Arial', 10, 'bold'),
                        relief='flat', padding=[10, 5])
        style.map('Green.TButton', background=[('active', '#388E3C'), ('pressed', '#1B5E20')])

        style.configure('Action.TButton', background='#0078d4', foreground='white', font=('Arial', 10, 'bold'),
                        relief='flat', padding=[10, 5])
        style.map('Action.TButton', background=[('active', '#005a9e'), ('pressed', '#003c6e')])

        # NUEVO ESTILO: Botones pequeños para el editor de notas
        style.configure('SmallAction.TButton', background='#0078d4', foreground='white', font=('Arial', 9, 'bold'),
                        relief='flat', padding=[5, 3])  # <-- Padding reducido
        style.map('SmallAction.TButton', background=[('active', '#005a9e'), ('pressed', '#003c6e')])

    def crear_seccion(self, parent_frame, titulo, acciones):
        """Función helper para crear secciones de etiquetas y botones."""
        if titulo:
            ttk.Label(parent_frame, text=titulo, font=('Arial', 11, 'bold')).pack(fill="x", pady=(10, 0), padx=5)

        frame_botones = ttk.Frame(parent_frame, style='TFrame')
        frame_botones.pack(fill="x", pady=5, padx=5)

        for texto_boton, comando in acciones:
            ttk.Button(frame_botones, text=texto_boton, command=comando, style='Green.TButton').pack(fill="x", pady=5)