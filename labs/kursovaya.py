import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import re


class UserManager:
    def __init__(self):
        self.users = {}

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def is_valid_username(self, username):
        if not ('a' <= username[0].lower() <= 'z'):
            return False
        for char in username:
            if not (('a' <= char.lower() <= 'z') or ('0' <= char <= '9')):
                return False
        return True

    def register(self, username, password):
        if username in self.users:
            return False, "Пользователь уже существует"

        if len(username) < 3:
            return False, "Логин минимум 3 символа"

        if not self.is_valid_username(username):
            if not ('a' <= username[0].lower() <= 'z'):
                return False, "Логин должен иметь только латинские буквы"
            for char in username:
                if not (('a' <= char.lower() <= 'z') or ('0' <= char <= '9')):
                    return False, "Только латинские буквы A-Z и цифры 0-9"
            return False, "Недопустимый формат логина"

        if len(password) < 4:
            return False, "Пароль минимум 4 символа"

        self.users[username] = self.hash_password(password)
        return True, "Регистрация успешна"

    def login(self, username, password):
        if username not in self.users:
            return False, "Пользователь не найден"
        if self.users[username] != self.hash_password(password):
            return False, "Неверный пароль"
        return True, "Вход выполнен"


class AuthWindow:
    def __init__(self, root):
        self.root = root
        self.user_manager = UserManager()
        self.current_user = None

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Волки и Овцы")
        self.root.geometry("300x300")

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Волки и Овцы", font=('Arial', 16)).pack(pady=20)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(pady=10, fill=tk.BOTH, expand=True)

        login_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(login_frame, text="Вход")

        ttk.Label(login_frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.login_user = ttk.Entry(login_frame)
        self.login_user.grid(row=0, column=1, pady=5)

        ttk.Label(login_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.login_pass = ttk.Entry(login_frame, show="*")
        self.login_pass.grid(row=1, column=1, pady=5)

        ttk.Button(login_frame, text="Войти", command=self.do_login).grid(row=2, column=0, columnspan=2, pady=10)

        reg_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(reg_frame, text="Регистрация")

        ttk.Label(reg_frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.reg_user = ttk.Entry(reg_frame)
        self.reg_user.grid(row=0, column=1, pady=5)

        ttk.Label(reg_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.reg_pass = ttk.Entry(reg_frame, show="*")
        self.reg_pass.grid(row=1, column=1, pady=5)

        ttk.Button(reg_frame, text="Зарегистрироваться", command=self.do_register).grid(row=2, column=0, columnspan=2,
                                                                                        pady=10)

        self.status = ttk.Label(main_frame, text="", foreground='red')
        self.status.pack()

    def do_login(self):
        user = self.login_user.get().strip()
        password = self.login_pass.get()

        if not user or not password:
            self.status.config(text="Заполните все поля")
            return

        success, msg = self.user_manager.login(user, password)
        if success:
            self.current_user = user
            self.status.config(text=f"Добро пожаловать, {user}!", foreground='green')
            self.root.after(1000, self.start_game)
        else:
            self.status.config(text=msg)

    def do_register(self):
        user = self.reg_user.get().strip()
        password = self.reg_pass.get()

        if not user or not password:
            self.status.config(text="Заполните все поля")
            return

        success, msg = self.user_manager.register(user, password)
        self.status.config(text=msg, foreground='green' if success else 'red')

        if success:
            self.notebook.select(0)
            self.login_user.delete(0, tk.END)
            self.login_user.insert(0, user)
            self.login_pass.focus()

    def start_game(self):
        self.root.withdraw()
        game_window = tk.Toplevel(self.root)
        game_window.title("Волки и Овцы")
        GameWindow(game_window, self.current_user, self)


class GameWindow:
    def __init__(self, root, username, auth_app):
        self.root = root
        self.username = username
        self.auth_app = auth_app

        self.board_size = 8
        self.cell_size = 60
        self.board_padding = 30
        self.board = [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'sheep'
        self.game_over = False
        self.selected_piece = None
        self.possible_moves = []

        self.setup_ui()
        self.setup_board()

    def setup_ui(self):
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(info_frame, text=f"Игрок: {self.username}").pack(side=tk.LEFT)
        ttk.Button(info_frame, text="Выйти", command=self.logout).pack(side=tk.RIGHT)

        self.status = ttk.Label(self.root, text="", font=('Arial', 12))
        self.status.pack(pady=5)

        canvas_width = self.board_size * self.cell_size + 2 * self.board_padding
        canvas_height = self.board_size * self.cell_size + 2 * self.board_padding
        self.canvas = tk.Canvas(self.root,
                                width=canvas_width,
                                height=canvas_height)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

        ttk.Button(self.root, text="Новая игра", command=self.new_game).pack(pady=5)

        self.update_status()

    def setup_board(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.board[i][j] = ''

        for col in [1, 3, 5, 7]:
            self.board[0][col] = 'wolf'

        self.board[7][4] = 'sheep'

        self.draw_board()

    def is_black(self, row, col):
        return (row + col) % 2 == 1

    def get_moves(self, row, col):
        piece = self.board[row][col]
        moves = []

        if piece == 'sheep':
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:  # wolf
            directions = [(1, -1), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            if (0 <= r < self.board_size and 0 <= c < self.board_size and
                    self.is_black(r, c) and self.board[r][c] == ''):
                moves.append((r, c))

        return moves

    def on_click(self, event):
        if self.game_over:
            return

        x = event.x - self.board_padding
        y = event.y - self.board_padding

        if x < 0 or y < 0 or x >= self.board_size * self.cell_size or y >= self.board_size * self.cell_size:
            return

        col = x // self.cell_size
        row = y // self.cell_size

        if not self.is_black(row, col):
            return

        if self.selected_piece:
            if self.move_piece(row, col):
                self.draw_board()
                self.update_status()
                return
            else:
                self.selected_piece = None
                self.possible_moves = []

        if self.board[row][col] and (
                (self.current_player == 'sheep' and self.board[row][col] == 'sheep') or
                (self.current_player == 'wolves' and self.board[row][col] == 'wolf')
        ):
            self.selected_piece = (row, col)
            self.possible_moves = self.get_moves(row, col)
            self.draw_board()
            self.update_status()

    def move_piece(self, to_row, to_col):
        if not self.selected_piece or (to_row, to_col) not in self.possible_moves:
            return False

        from_row, from_col = self.selected_piece
        piece = self.board[from_row][from_col]
        self.board[from_row][from_col] = ''
        self.board[to_row][to_col] = piece

        self.check_win()

        if not self.game_over:
            self.current_player = 'wolves' if self.current_player == 'sheep' else 'sheep'

        self.selected_piece = None
        self.possible_moves = []
        return True

    def check_win(self):
        if any(self.board[0][col] == 'sheep' for col in range(self.board_size)):
            self.game_over = True
            messagebox.showinfo("Игра окончена", "Победила овца!")
            return

        sheep_pos = None
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 'sheep':
                    sheep_pos = (row, col)
                    break

        if not sheep_pos or not self.get_moves(sheep_pos[0], sheep_pos[1]):
            self.game_over = True
            messagebox.showinfo("Игра окончена", "Победили волки!")

    def draw_board(self):
        self.canvas.delete("all")

        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        for col in range(self.board_size):
            x = self.board_padding + col * self.cell_size + self.cell_size // 2
            y = self.board_padding // 2
            self.canvas.create_text(x, y, text=letters[col], font=('Arial', 12, 'bold'))

        for col in range(self.board_size):
            x = self.board_padding + col * self.cell_size + self.cell_size // 2
            y = self.board_padding + self.board_size * self.cell_size + self.board_padding // 2
            self.canvas.create_text(x, y, text=letters[col], font=('Arial', 12, 'bold'))

        for row in range(self.board_size):
            x = self.board_padding // 2
            y = self.board_padding + row * self.cell_size + self.cell_size // 2
            self.canvas.create_text(x, y, text=str(8 - row), font=('Arial', 12, 'bold'))

        for row in range(self.board_size):
            x = self.board_padding + self.board_size * self.cell_size + self.board_padding // 2
            y = self.board_padding + row * self.cell_size + self.cell_size // 2
            self.canvas.create_text(x, y, text=str(8 - row), font=('Arial', 12, 'bold'))

        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = self.board_padding + col * self.cell_size
                y1 = self.board_padding + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = '#F0D9B5' if (row + col) % 2 == 0 else '#B58863'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

                if self.selected_piece and (row, col) in self.possible_moves:
                    self.canvas.create_oval(x1 + 15, y1 + 15, x2 - 15, y2 - 15, fill='green')

                if self.selected_piece == (row, col):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline='blue', width=3)

                if self.board[row][col] == 'wolf':
                    self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill='black')
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="В", fill='white', font=('Arial', 12))
                elif self.board[row][col] == 'sheep':
                    self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill='white', outline='black')
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="О", fill='black', font=('Arial', 12))

    def update_status(self):
        if self.game_over:
            self.status.config(text="Игра завершена")
        else:
            player = "Овца" if self.current_player == 'sheep' else "Волки"
            self.status.config(text=f"Ход: {player}")

    def new_game(self):
        self.board = [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'sheep'
        self.game_over = False
        self.selected_piece = None
        self.possible_moves = []
        self.setup_board()
        self.update_status()

    def logout(self):
        self.root.destroy()
        self.auth_app.root.deiconify()


def main():
    root = tk.Tk()
    app = AuthWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()