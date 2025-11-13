import tkinter as tk
from tkinter import messagebox
import random

my_board = [[0 for _ in range(10)] for _ in range(10)]
ai_board = [[0 for _ in range(10)] for _ in range(10)]

my_hits = 0
ai_hits = 0

game_mode = 'placing'
ships_to_place = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
placing_horizontal = True

ai_targeting = None
ai_direction = None


def can_place(board, row, col, size, horizontal):
    if horizontal:
        if col + size > 10: return False
        for j in range(col, col + size):
            if board[row][j] != 0: return False
    else:
        if row + size > 10: return False
        for i in range(row, row + size):
            if board[i][col] != 0: return False
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if horizontal:
                for j in range(col, col + size):
                    ni, nj = row + di, j + dj
                    if 0 <= ni < 10 and 0 <= nj < 10:
                        if board[ni][nj] == 1: return False
            else:
                for i in range(row, row + size):
                    ni, nj = i + di, col + dj
                    if 0 <= ni < 10 and 0 <= nj < 10:
                        if board[ni][nj] == 1: return False
    return True


def place_ship(board, row, col, size, horizontal):
    if horizontal:
        for j in range(col, col + size): board[row][j] = 1
    else:
        for i in range(row, row + size): board[i][col] = 1


def draw_board(board, buttons, is_ai_board=False):
    for i in range(10):
        for j in range(10):
            val = board[i][j]
            btn = buttons[i][j]
            if is_ai_board and val == 1:
                btn.config(text="", bg="SystemButtonFace", relief="raised")
            elif val == 0:
                if board is my_board and game_mode == 'placing':
                    btn.config(bg="SystemButtonFace", relief="raised")
                else:
                    btn.config(bg="SystemButtonFace", relief="raised")
            elif val == 1:
                btn.config(text="●", fg="#E74C3C", bg="SystemButtonFace")
            elif val == 2:
                btn.config(text="✸", fg="#F1C40F", bg="#E74C3C", relief="sunken")
            elif val == 3:
                btn.config(text="○", fg="#7F8C8D", bg="SystemButtonFace", relief="sunken")


def update_title():
    if game_mode == 'placing':
        left = len(ships_to_place)
        window.title(f"Морской бой — Расстановка ({left} кораблей осталось)")
    else:
        window.title(f"Морской бой — Счёт: Игрок {my_hits} : {ai_hits} ИИ")


def rotate_ship():
    global placing_horizontal
    placing_horizontal = not placing_horizontal
    dir_text = "горизонтально" if placing_horizontal else "вертикально"
    current = ships_to_place[0] if ships_to_place else 0
    window.title(f"Морской бой — Ставим {current}-палубный ({dir_text})")


def place_player_ship(row, col):
    global ships_to_place
    if game_mode != 'placing' or not ships_to_place:
        return
    size = ships_to_place[0]
    if can_place(my_board, row, col, size, placing_horizontal):
        place_ship(my_board, row, col, size, placing_horizontal)
        ships_to_place.pop(0)
        draw_board(my_board, my_buttons)
        if ships_to_place:
            rotate_ship()
        else:
            window.title("Морской бой — Все корабли расставлены! Нажмите «Начать битву»")
    else:
        messagebox.showwarning("Невозможно разместить", "Корабль нельзя разместить здесь!")


def get_ai_shot():
    global ai_targeting, ai_direction

    if ai_targeting:
        r, c = ai_targeting
        directions = []
        if ai_direction is None:
            directions = [('up', r - 1, c), ('down', r + 1, c), ('left', r, c - 1), ('right', r, c + 1)]
        else:
            if ai_direction == 'up':
                directions = [('up', r - 1, c)]
            elif ai_direction == 'down':
                directions = [('down', r + 1, c)]
            elif ai_direction == 'left':
                directions = [('left', r, c - 1)]
            elif ai_direction == 'right':
                directions = [('right', r, c + 1)]

        for d, nr, nc in directions:
            if 0 <= nr < 10 and 0 <= nc < 10 and my_board[nr][nc] not in (2, 3):
                ai_direction = d
                return nr, nc
        all_dirs = [('up', r - 1, c), ('down', r + 1, c), ('left', r, c - 1), ('right', r, c + 1)]
        random.shuffle(all_dirs)
        for d, nr, nc in all_dirs:
            if 0 <= nr < 10 and 0 <= nc < 10 and my_board[nr][nc] not in (2, 3):
                ai_direction = d
                return nr, nc
        ai_targeting = None
        ai_direction = None

    candidates = [(i, j) for i in range(10) for j in range(10)
                  if my_board[i][j] not in (2, 3) and (i + j) % 2 == 0]
    if candidates:
        return random.choice(candidates)
    fallback = [(i, j) for i in range(10) for j in range(10) if my_board[i][j] not in (2, 3)]
    return random.choice(fallback) if fallback else (0, 0)


def ai_move():
    global ai_hits, ai_targeting, ai_direction
    if game_mode != 'playing':
        return
    row, col = get_ai_shot()
    hit = (my_board[row][col] == 1)
    my_board[row][col] = 2 if hit else 3
    ai_hits += 1 if hit else 0
    if hit:
        if ai_targeting is None:
            ai_targeting = (row, col)
            ai_direction = None
        destroyed = True
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 10 and 0 <= nc < 10 and my_board[nr][nc] == 1:
                destroyed = False
                break
        if destroyed:
            ai_targeting = None
            ai_direction = None
    else:
        pass

    draw_board(my_board, my_buttons)
    update_title()

    if ai_hits == 20:
        messagebox.showinfo("Поражение", "ИИ победил! Все ваши корабли потоплены.")


def on_my_click(row, col):
    if game_mode == 'placing':
        place_player_ship(row, col)


def on_ai_click(row, col):
    global my_hits
    if game_mode != 'playing' or ai_board[row][col] in (2, 3):
        return
    hit = (ai_board[row][col] == 1)
    ai_board[row][col] = 2 if hit else 3
    my_hits += 1 if hit else 0
    draw_board(ai_board, ai_buttons, is_ai_board=True)
    update_title()
    if my_hits == 20:
        messagebox.showinfo("Победа!", "Вы победили!")
        return
    window.after(500, ai_move)


def start_game():
    global game_mode, my_hits, ai_hits, ai_targeting, ai_direction

    if game_mode == 'playing':
        messagebox.showinfo("Игра уже идет", "Битва уже началась!")
        return

    if ships_to_place:
        messagebox.showwarning("Внимание", "Расставьте все корабли!")
        return

    for i in range(10):
        for j in range(10):
            ai_board[i][j] = 0

    for size in [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            r, c = random.randint(0, 9), random.randint(0, 9)
            h = random.choice([True, False])
            if can_place(ai_board, r, c, size, h):
                place_ship(ai_board, r, c, size, h)
                placed = True
            attempts += 1

        if not placed:
            messagebox.showerror("Ошибка", "Не удалось разместить корабли ИИ. Попробуйте еще раз.")
            return

    game_mode = 'playing'
    draw_board(my_board, my_buttons)
    draw_board(ai_board, ai_buttons, is_ai_board=True)
    update_title()


window = tk.Tk()
window.title("Морской бой — Ставим 4-х палубный (горизонтально)")

my_frame = tk.Frame(window)
my_frame.grid(row=0, column=0, padx=15, pady=10)
ai_frame = tk.Frame(window)
ai_frame.grid(row=0, column=1, padx=15, pady=10)

tk.Label(my_frame, text="ВАШ ФЛОТ", fg="#3498DB", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=10)
tk.Label(ai_frame, text="ВРАЖЕСКИЙ ФЛОТ", fg="#E74C3C", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=10)

my_buttons = []
for i in range(10):
    row_buttons = []
    for j in range(10):
        btn = tk.Button(my_frame, width=3, height=1, font=("Arial", 8),
                        relief="raised", bd=1)
        btn.grid(row=i + 1, column=j, padx=1, pady=1)
        btn.config(command=lambda i=i, j=j: on_my_click(i, j))
        row_buttons.append(btn)
    my_buttons.append(row_buttons)

ai_buttons = []
for i in range(10):
    row_buttons = []
    for j in range(10):
        btn = tk.Button(ai_frame, width=3, height=1, font=("Arial", 8),
                        relief="raised", bd=1)
        btn.grid(row=i + 1, column=j, padx=1, pady=1)
        btn.config(command=lambda i=i, j=j: on_ai_click(i, j))
        row_buttons.append(btn)
    ai_buttons.append(row_buttons)

control_frame = tk.Frame(window)
control_frame.grid(row=1, column=0, columnspan=2, pady=15)

tk.Button(control_frame, text="Повернуть корабль", command=rotate_ship,
          font=("Arial", 9)).grid(row=0, column=0, padx=10)
tk.Button(control_frame, text="Начать битву", command=start_game,
          font=("Arial", 9,)).grid(row=0, column=1, padx=10)

draw_board(my_board, my_buttons)

window.mainloop()