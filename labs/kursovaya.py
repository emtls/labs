import tkinter as tk
from tkinter import messagebox


class WolvesAndSheepGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Волки и Овцы")
        self.root.resizable(False, False)

        self.board_size = 8
        self.cell_size = 60

        self.board = [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'sheep'
        self.game_over = False
        self.winner = None
        self.selected_piece = None
        self.possible_moves = []

        self.create_widgets()
        self.setup_board()

    def create_widgets(self):
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)

        self.status_label = tk.Label(self.info_frame, text="", font=('Arial', 14))
        self.status_label.pack()

        self.canvas = tk.Canvas(self.root,
                                width=self.board_size * self.cell_size,
                                height=self.board_size * self.cell_size,
                                bg='white')
        self.canvas.pack(pady=10)

        self.restart_button = tk.Button(self.root, text="Новая игра",
                                        command=self.restart_game, font=('Arial', 12))
        self.restart_button.pack(pady=5)

        self.canvas.bind("<Button-1>", self.on_click)

        self.update_status()

    def setup_board(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.board[i][j] = ''

        wolf_positions = [(0, 1), (0, 3), (0, 5), (0, 7)]
        for row, col in wolf_positions:
            self.board[row][col] = 'wolf'

        self.board[7][4] = 'sheep'

        self.draw_board()

    def is_black_cell(self, row, col):
        return (row + col) % 2 == 1

    def is_valid_position(self, row, col):
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def get_possible_moves(self, row, col):
        piece = self.board[row][col]
        moves = []

        if piece == 'sheep':
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if (self.is_valid_position(new_row, new_col) and
                        self.is_black_cell(new_row, new_col) and
                        self.board[new_row][new_col] == ''):
                    moves.append((new_row, new_col))

        elif piece == 'wolf':
            directions = [(1, -1), (1, 1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if (self.is_valid_position(new_row, new_col) and
                        self.is_black_cell(new_row, new_col) and
                        self.board[new_row][new_col] == ''):
                    moves.append((new_row, new_col))

        return moves

    def select_piece(self, row, col):
        if self.game_over:
            return False

        piece = self.board[row][col]

        if (self.current_player == 'sheep' and piece == 'sheep') or \
                (self.current_player == 'wolves' and piece == 'wolf'):
            self.selected_piece = (row, col)
            self.possible_moves = self.get_possible_moves(row, col)
            return True

        return False

    def move_piece(self, to_row, to_col):
        if not self.selected_piece or self.game_over:
            return False

        from_row, from_col = self.selected_piece

        if (to_row, to_col) in self.possible_moves:
            piece = self.board[from_row][from_col]
            self.board[from_row][from_col] = ''
            self.board[to_row][to_col] = piece

            self.check_win_conditions()

            if not self.game_over:
                self.current_player = 'wolves' if self.current_player == 'sheep' else 'sheep'

            self.selected_piece = None
            self.possible_moves = []
            return True

        return False

    def check_win_conditions(self):
        for col in range(self.board_size):
            if self.board[0][col] == 'sheep':
                self.game_over = True
                self.winner = 'sheep'
                self.show_winner_message()
                return

        sheep_pos = None
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 'sheep':
                    sheep_pos = (row, col)
                    break
            if sheep_pos:
                break

        if not sheep_pos:
            self.game_over = True
            self.winner = 'wolves'
            self.show_winner_message()
            return

        sheep_moves = self.get_possible_moves(sheep_pos[0], sheep_pos[1])
        if not sheep_moves:
            self.game_over = True
            self.winner = 'wolves'
            self.show_winner_message()
            return

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        blocked_count = 0
        possible_directions = 0

        for dr, dc in directions:
            new_row, new_col = sheep_pos[0] + dr, sheep_pos[1] + dc
            if self.is_valid_position(new_row, new_col) and self.is_black_cell(new_row, new_col):
                possible_directions += 1
                if self.board[new_row][new_col] == 'wolf' or not self.is_black_cell(new_row, new_col):
                    blocked_count += 1

        if possible_directions > 0 and blocked_count == possible_directions:
            self.game_over = True
            self.winner = 'wolves'
            self.show_winner_message()

    def show_winner_message(self):
        winner_text = "Овца" if self.winner == 'sheep' else "Волки"
        messagebox.showinfo("Игра окончена!", f"Победили: {winner_text}!")

    def on_click(self, event):
        if self.game_over:
            return

        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if not self.is_black_cell(row, col):
            return

        if self.selected_piece:
            if self.move_piece(row, col):
                self.draw_board()
                self.update_status()
                return
            else:
                self.selected_piece = None
                self.possible_moves = []

        if self.select_piece(row, col):
            self.draw_board()
            self.update_status()
        else:
            self.selected_piece = None
            self.possible_moves = []
            self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")

        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = '#F0D9B5' if (row + col) % 2 == 0 else '#B58863'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

                if self.selected_piece and (row, col) in self.possible_moves:
                    self.canvas.create_oval(x1 + 15, y1 + 15, x2 - 15, y2 - 15,
                                            fill='green', outline='')

                if self.selected_piece == (row, col):
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                 outline='blue', width=3)

                if self.board[row][col] == 'wolf':
                    self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10,
                                            fill='black', outline='')
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                            text="В", fill='white', font=('Arial', 14, 'bold'))

                elif self.board[row][col] == 'sheep':
                    self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10,
                                            fill='white', outline='black')
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                            text="О", fill='black', font=('Arial', 14, 'bold'))

    def update_status(self):
        if self.game_over:
            winner_text = "Овца" if self.winner == 'sheep' else "Волки"
            self.status_label.config(text=f"Игра окончена! Победили: {winner_text}",
                                     fg='red')
        else:
            player_text = "Овца" if self.current_player == 'sheep' else "Волки"
            self.status_label.config(text=f"Сейчас ход: {player_text}",
                                     fg='blue')

    def restart_game(self):
        self.current_player = 'sheep'
        self.game_over = False
        self.winner = None
        self.selected_piece = None
        self.possible_moves = []
        self.setup_board()
        self.update_status()

def main():
    root = tk.Tk()
    game = WolvesAndSheepGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()