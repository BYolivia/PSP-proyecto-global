# Módulo: logica/T2/buscaMinas.py

import random


class BuscaMinas:
    """
    Lógica de un Buscaminas con regla de 'primer clic seguro' y banderas.
    """

    def __init__(self, rows=16, cols=16, mines=40):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = []  # El tablero real (minas: 'M', números: 0-8)
        self.revealed = []  # El estado visible (True/False)
        self.flagged = []  # Estado de la bandera (True/False)
        self.first_click = True  # Bandera para detectar el primer clic
        self.game_over = False
        self.won = False
        self.setup_board()

    def setup_board(self):
        """Inicializa un tablero vacío y el estado de juego, esperando el primer clic."""

        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.game_over = False
        self.won = False
        self.first_click = True

        print(f"[Buscaminas] Tablero vacío {self.rows}x{self.cols} listo. Esperando primer clic seguro.")

    def _place_mines_safely(self, start_r, start_c):
        """
        Coloca las minas *después* del primer clic,
        garantizando que la zona 3x3 alrededor de (start_r, start_c) esté libre.
        """

        # 1. Definir posiciones prohibidas (3x3 alrededor del clic inicial)
        safe_positions = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = start_r + dr, start_c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    safe_positions.add((nr, nc))

        available_positions = []
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in safe_positions:
                    available_positions.append((r, c))

        # 2. Elegir la posición de las minas
        mine_positions = random.sample(available_positions, self.mines)

        # 3. Colocar Minas
        for r, c in mine_positions:
            self.board[r][c] = 'M'

        # 4. Calcular números adyacentes
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != 'M':
                    self.board[r][c] = self._count_adjacent_mines(r, c)

        print(f"[Buscaminas] Minas y números colocados. Zona de clic ({start_r},{start_c}) segura.")

    def _count_adjacent_mines(self, r, c):
        """Cuenta el número de minas en las 8 casillas adyacentes."""
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc

                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.board[nr][nc] == 'M':
                        count += 1
        return count

    def toggle_flag(self, r, c):
        """
        Alterna el estado de la bandera en una celda.
        Solo se permite si la celda no ha sido revelada y el juego no ha terminado.
        Retorna True si el estado del tablero se modificó, False en caso contrario.
        """
        if self.game_over or self.revealed[r][c]:
            return False

        # Alternar la bandera
        self.flagged[r][c] = not self.flagged[r][c]
        return True

    def reveal_cell(self, r, c):
        """
        Revela una celda al ser clickeada (clic izquierdo).
        Retorna: (str, bool) -> (Mensaje, ¿Juego terminado?)
        """
        if self.game_over or self.revealed[r][c]:
            return "", False

        # IMPEDIR REVELAR SI HAY BANDERA COLOCADA
        if self.flagged[r][c]:
            return "❌ Debes quitar la bandera para revelar la celda.", False

        # Si es el primer clic, colocamos las minas de forma segura
        if self.first_click:
            self._place_mines_safely(r, c)
            self.first_click = False

        self.revealed[r][c] = True

        # Caso 1: Mina
        if self.board[r][c] == 'M':
            self.game_over = True
            return "💥 ¡BOOM! Juego terminado.", True

        # Caso 2: Cero (Expansión)
        elif self.board[r][c] == 0:
            self._expand_zeros(r, c)

        # Caso 3: Número (Solo revelar)

        # Verificar victoria después de la jugada
        if self._check_win():
            self.game_over = True
            self.won = True
            return "🏆 ¡Ganaste! Has revelado todas las casillas seguras.", True

        return "", False

    def _expand_zeros(self, r, c):
        """Algoritmo de inundación para revelar áreas vacías (BFS)."""

        queue = [(r, c)]

        while queue:
            curr_r, curr_c = queue.pop(0)

            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = curr_r + dr, curr_c + dc

                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if not self.revealed[nr][nc]:
                            # Si hay una bandera, no la quitamos, pero no la propagamos
                            if self.flagged[nr][nc]:
                                continue

                            self.revealed[nr][nc] = True

                            if self.board[nr][nc] == 0:
                                queue.append((nr, nc))

    def _check_win(self):
        """Verifica si todas las casillas no-mina han sido reveladas."""
        safe_cells_revealed = 0
        total_safe_cells = self.rows * self.cols - self.mines

        for r in range(self.rows):
            for c in range(self.cols):
                if self.revealed[r][c] and self.board[r][c] != 'M':
                    safe_cells_revealed += 1

        return safe_cells_revealed == total_safe_cells

    def get_board_state(self):
        """Retorna una matriz con el estado visible del juego (para la UI), incluyendo banderas y el resultado final."""
        state = []

        for r in range(self.rows):
            row = []
            for c in range(self.cols):

                if self.revealed[r][c]:
                    # 1. Revelada: muestra el contenido real
                    row.append(str(self.board[r][c]))
                elif self.flagged[r][c] and not self.game_over:
                    # 2. Bandera (juego en curso)
                    row.append('F')
                elif self.game_over:
                    # 3. Analizar estado final (solo si el juego terminó)
                    if self.flagged[r][c]:
                        if self.board[r][c] == 'M':
                            # 3a. Bandera CORRECTA
                            row.append('F+')
                        else:
                            # 3b. Bandera INCORRECTA (marcada en celda segura)
                            row.append('F-')
                    elif self.board[r][c] == 'M':
                        # 3c. Mina sin marcar
                        row.append('M')
                    else:
                        # 3d. Celda segura, sin revelar y sin bandera
                        row.append(' ')
                else:
                    # 4. Celda oculta normal (juego en curso)
                    row.append(' ')

            state.append(row)
        return state