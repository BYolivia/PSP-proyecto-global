# Módulo: vista/panel_lateral.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from logica.controlador import accion_placeholder, getPlataforma
from logica.T1.backup import accion_backup_t1
from logica.T1.runVScode import abrir_vscode


class PanelLateral(ttk.Frame):
    """Contiene el menú de botones y entradas para las tareas de T1."""

    def __init__(self, parent, central_panel=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.central_panel = central_panel  # Guardamos la referencia

        # ❌ ELIMINAR ESTA LÍNEA: self.pack(fill="y", padx=5, pady=5)

        self.configurar_estilos_locales(parent)

        # Entrada superior (amarilla)
        ttk.Entry(self, width=25, style='Yellow.TEntry').pack(fill="x", pady=10, padx=5, ipady=3)

        # 1. Área de Extracción/Navegación
        acciones_extraccion = [
            ("Extraer datos", self.manejar_extraccion_datos),
            ("Navegar", lambda: accion_placeholder("Navegar")),
            ("Buscar API Google", lambda: accion_placeholder("Buscar API Google"))
        ]
        self.crear_seccion(self, titulo="", acciones=acciones_extraccion)

        # 2. Área de Aplicaciones
        acciones_aplicaciones = [
            ("Visual Code", abrir_vscode),
            ("App2", lambda: accion_placeholder("App2")),
            ("App3", lambda: accion_placeholder("App3"))
        ]
        self.crear_seccion(self, titulo="Aplicaciones", acciones=acciones_aplicaciones)

        # 3. Área de Procesos Batch
        acciones_batch = [
            ("Copias de seguridad", self.manejar_backup)
        ]
        self.crear_seccion(self, titulo="Procesos batch", acciones=acciones_batch)

        tk.Frame(self, height=1).pack(expand=True, fill="both")

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
            messagebox.showinfo("Backup Completado", message)
        else:
            messagebox.showerror("Error en el Backup", message)

    def configurar_estilos_locales(self, parent):
        """Configura estilos para los widgets del panel lateral."""
        style = ttk.Style(parent)
        style.configure('Yellow.TEntry', fieldbackground='#fff8e1', foreground='#333333', padding=[5, 5],
                        relief='solid', borderwidth=1)
        style.configure('Green.TButton', background='#4CAF50', foreground='white', font=('Arial', 10, 'bold'),
                        relief='flat', padding=[10, 5])
        style.map('Green.TButton', background=[('active', '#388E3C'), ('pressed', '#1B5E20')])

    def crear_seccion(self, parent_frame, titulo, acciones):
        """Función helper para crear secciones de etiquetas y botones."""
        if titulo:
            ttk.Label(parent_frame, text=titulo, font=('Arial', 11, 'bold')).pack(fill="x", pady=(10, 0), padx=5)

        frame_botones = ttk.Frame(parent_frame, style='TFrame')
        frame_botones.pack(fill="x", pady=5, padx=5)

        for texto_boton, comando in acciones:
            ttk.Button(frame_botones, text=texto_boton, command=comando, style='Green.TButton').pack(fill="x", pady=5)