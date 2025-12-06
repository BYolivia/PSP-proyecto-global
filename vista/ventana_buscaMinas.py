# Módulo: vista/ventana_buscaMinas.py

import tkinter as tk
from tkinter import ttk, messagebox
# 🔑 Importamos la lógica del minijuego
from logica.T2.buscaMinas import BuscaMinas
# 🔑 Importamos la configuración de estilos
from vista.config import *


class VentanaBuscaMinas(tk.Toplevel):
    """
    Ventana secundaria (tk.Toplevel) para el Buscaminas.
    Es no-modal y permite interactuar con la VentanaPrincipal.
    """

    def __init__(self, parent):
        # Inicializar como ventana secundaria
        super().__init__(parent)
        self.title("💣 Buscaminas - App3")
        self.geometry("500x600")
        self.resizable(False, False)

        # 1. Inicializar la lógica del juego (16x16, 40 minas)
        self.game = BuscaMinas(rows=16, cols=16, mines=40)
        self.buttons = {}  # Almacena las referencias a los botones (celdas)

        # Variables de control de UI
        self.feedback_var = tk.StringVar(value="Haz clic para empezar...")

        # 2. Configurar el layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Manejar el cierre

    def create_widgets(self):
        """Crea el marco superior de control y el marco del tablero."""

        # --- Marco Superior de Control ---
        control_frame = ttk.Frame(self, padding=10)
        control_frame.grid(row=0, column=0, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)

        # Botón Nuevo Juego (Usamos ttk para botones fuera del tablero)
        ttk.Button(control_frame, text="🔄 Nuevo Juego", command=self.reset_game, style='Action.TButton').grid(
            row=0, column=0, padx=(0, 5), sticky="w")

        # Feedback (Mensajes de éxito/derrota)
        ttk.Label(control_frame, textvariable=self.feedback_var, font=FUENTE_NEGOCIOS).grid(
            row=0, column=1, padx=(5, 0), sticky="e")

        # --- Marco del Tablero ---
        self.board_frame = ttk.Frame(self, padding=5, style='TFrame')
        self.board_frame.grid(row=1, column=0, sticky="nsew")

        self.draw_board()

    def draw_board(self):
        """Crea la matriz de botones que representan las celdas del buscaminas."""

        # Limpiar y reconfigurar el frame
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.buttons = {}

        # Asegurar que los botones se expandan uniformemente
        for i in range(self.game.rows):
            self.board_frame.grid_rowconfigure(i, weight=1)
        for j in range(self.game.cols):
            self.board_frame.grid_columnconfigure(j, weight=1)

        for r in range(self.game.rows):
            for c in range(self.game.cols):
                # USANDO tk.Button ESTÁNDAR para la configuración dinámica de colores
                btn = tk.Button(
                    self.board_frame,
                    text="",
                    width=2,
                    height=1,
                    relief=tk.RAISED,
                    background='gray70',
                    activebackground='gray50',
                    # Clic Izquierdo (Button-1): revelar (usando 'command')
                    command=lambda row=r, col=c: self.handle_click(row, col)
                )
                btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                self.buttons[(r, c)] = btn

                # VINCULAR CLIC DERECHO (Button-3) a handle_flag
                btn.bind("<Button-3>", lambda event, row=r, col=c: self.handle_flag(row, col))

    def handle_click(self, r, c):
        """Maneja el clic Izquierdo para revelar."""

        if self.game.game_over:
            return

        message, game_over = self.game.reveal_cell(r, c)

        # 1. Actualizar el tablero con el nuevo estado
        self.update_ui_board()

        # 2. Manejar el estado final del juego
        if game_over:
            self.feedback_var.set(message)
            self.show_end_game()

        else:
            self.feedback_var.set("¡Cuidado! Minando...")
            # Mostrar mensaje si la lógica impidió la revelación (ej: por bandera)
            if message:
                self.feedback_var.set(message)

    def handle_flag(self, r, c):
        """
        Maneja el clic Derecho para colocar/quitar la bandera.
        """
        if self.game.game_over:
            return

        # Llama a la lógica para alternar la bandera
        if self.game.toggle_flag(r, c):
            self.update_ui_board()  # Solo actualizamos si el estado de la bandera cambió

    def update_ui_board(self):
        """Recorre el estado lógico y actualiza el texto, color y estado de los botones."""
        state = self.game.get_board_state()
        revealed_bg = 'lightgray'

        for r in range(self.game.rows):
            for c in range(self.game.cols):
                text = state[r][c]
                btn = self.buttons[(r, c)]

                # Estado por defecto (oculto, levantado)
                btn.config(text="", background='gray70', foreground='black', relief=tk.RAISED, state=tk.NORMAL)

                if text == 'F':
                    # Bandera (juego en curso)
                    btn.config(text="🚩", foreground='blue', relief=tk.RAISED, state=tk.NORMAL)

                # 🔑 NUEVO: Manejo de estado final de banderas
                elif self.game.game_over:
                    btn.config(state=tk.DISABLED)  # Deshabilitar todos los botones

                    if text == 'F+':
                        # Bandera Correcta (Mina marcada)
                        btn.config(text="✅", background='green', foreground='white', relief=tk.RAISED)
                    elif text == 'F-':
                        # Bandera Incorrecta (Celda segura marcada)
                        btn.config(text="❌", background='orange', foreground='white', relief=tk.RAISED)
                    elif text == 'M':
                        # Mina sin marcar (se revela al final)
                        btn.config(text="💣", background='black', foreground='white', relief=tk.SUNKEN)
                    # El resto de celdas se manejan a continuación si están reveladas.

                if self.game.revealed[r][c]:
                    # Celda revelada
                    btn.config(relief=tk.SUNKEN, state=tk.DISABLED)

                    if text == 'M':
                        # Mina clickeada (rojo, mina detonadora)
                        btn.config(text="💣", background='red', foreground='white')

                    elif text != '0':
                        # Número
                        btn.config(
                            text=text,
                            background=revealed_bg,
                            foreground=self._get_number_color(int(text))
                        )
                    else:
                        # Cero
                        btn.config(text="", background=revealed_bg)

    def show_end_game(self):
        """Muestra el estado final, revela el tablero completo y deshabilita clics."""

        self.update_ui_board()

        # Asegurar el deshabilitado final (redundante pero seguro)
        for btn in self.buttons.values():
            btn.config(state=tk.DISABLED)

    def reset_game(self):
        """Reinicia el juego lógico y recrea el tablero visual."""
        self.game.setup_board()
        self.feedback_var.set("¡A jugar! Encontrando minas en 16x16...")
        self.draw_board()
        self.update_ui_board()

    def _get_number_color(self, number):
        """Retorna un color basado en el número de la mina."""
        colors = {
            1: 'blue',
            2: 'green',
            3: 'red',
            4: 'purple',
            5: 'maroon',
            6: 'turquoise',
            7: 'black',
            8: 'gray'
        }
        return colors.get(number, 'black')

    def on_close(self):
        """Maneja el evento de cierre de la ventana Toplevel."""
        print("[Minigame] Cerrando ventana Buscaminas.")
        self.destroy()