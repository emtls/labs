import tkinter as tk
from tkinter import messagebox

window = tk.Tk()
window.title("Крестики-нолики")

board = ["", "", "", "", "", "", "", "", ""]

buttons = []

def human_move(i):
    if board[i] == "":
        board[i] = "X"
        buttons[i].config(text="X")

        if check_win("X"):
            messagebox.showinfo("Игра окончена", "Вы выиграли!")
            window.destroy()
        elif "" not in board:
            messagebox.showinfo("Игра окончена", "Ничья!")
            window.destroy()
        else:
            bot_move()

def bot_move():
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            if check_win("O"):
                buttons[i].config(text="O")
                messagebox.showinfo("Игра окончена", "Бот выиграл!")
                window.destroy()
                return
            board[i] = ""

    for i in range(9):
        if board[i] == "":
            board[i] = "X"
            if check_win("X"):
                board[i] = "O"
                buttons[i].config(text="O")
                return
            board[i] = ""
#центр, потом углы, потом остальное
    best_cells = [4, 0, 2, 6, 8, 1, 3, 5, 7]
    for i in best_cells:
        if board[i] == "":
            board[i] = "O"
            buttons[i].config(text="O")
            break

    if check_win("O"):
        messagebox.showinfo("Игра окончена", "Бот выиграл!")
        window.destroy()
    elif "" not in board:
        messagebox.showinfo("Игра окончена", "Ничья!")
        window.destroy()

def check_win(player):
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # строки
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # столбцы
        [0, 4, 8], [2, 4, 6]  # диагонали
    ]
    for combo in wins:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] == player:
            return True
    return False

for i in range(9):
    button = tk.Button(window, text="", font=("Arial", 24), width=5, height=2,
                       command=lambda i=i: human_move(i))
    button.grid(row=i // 3, column=i % 3)
    buttons.append(button)

window.mainloop()