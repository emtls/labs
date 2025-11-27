import tkinter as tk
from tkinter import messagebox
import random
import time


class MazeGame:
    def __init__(self, root, cols=21, rows=15, cell_size=30, num_exits=3):
        self.root = root
        self.root.title("Паук в лабиринте")
        self.cols = cols if cols % 2 == 1 else cols + 1
        self.rows = rows if rows % 2 == 1 else rows + 1
        self.cell_size = cell_size
        self.num_exits = num_exits

        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size,
                                height=self.rows * self.cell_size, bg="#f8f9fa")
        self.canvas.pack(pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text="Новая игра", command=self.reset_game).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Запустить", command=self.start_dfs).pack(side=tk.LEFT, padx=5)

        self.timer_label = tk.Label(root, text="Время: 0.0 с", font=("Arial", 12))
        self.timer_label.pack()

        self.reset_game()

    def reset_game(self):
        if hasattr(self, 'moving') and self.moving:
            return
        self.game_over = False
        self.moving = False
        self.elapsed_time = 0.0
        self.start_time = None
        self.timer_label.config(text="Время: 0.0 с")
        self.generate_maze()
        self.draw_maze()
        self.draw_player()
        self.canvas.delete("trail")

    def generate_maze(self):
        self.maze = [[True for _ in range(self.cols)] for _ in range(self.rows)]

        def dfs(x, y):
            self.maze[y][x] = False
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.cols - 1 and 0 < ny < self.rows - 1 and self.maze[ny][nx]:
                    self.maze[y + dy // 2][x + dx // 2] = False
                    dfs(nx, ny)

        dfs(1, 1)

        passages = []
        for y in range(1, self.rows - 1):
            for x in range(1, self.cols - 1):
                if not self.maze[y][x]:
                    passages.append((x, y))

        if len(passages) >= self.num_exits + 1:
            self.exit_positions = random.sample(passages, self.num_exits)

            start_candidates = [p for p in passages if p not in self.exit_positions]
            self.player_pos = random.choice(start_candidates) if start_candidates else (1, 1)
        else:
            self.player_pos = (1, 1)
            self.exit_positions = [(self.cols - 2, self.rows - 2)]

    def draw_maze(self):
        self.canvas.delete("all")
        for y in range(self.rows):
            for x in range(self.cols):
                cx, cy = x * self.cell_size, y * self.cell_size
                if self.maze[y][x]:
                    self.canvas.create_rectangle(
                        cx, cy, cx + self.cell_size, cy + self.cell_size,
                        fill="black", outline=""
                    )

        for i, (ex, ey) in enumerate(self.exit_positions):
            cx = ex * self.cell_size + self.cell_size // 2
            cy = ey * self.cell_size + self.cell_size // 2
            color = "red" if i == 0 else "green" if i == 1 else "blue"
            self.canvas.create_text(cx, cy, text=f"Выход {i + 1}", fill=color, font=("Arial", 10, "bold"))

    def draw_player(self):
        if hasattr(self, '_player_id'):
            self.canvas.delete(self._player_id)
        x, y = self.player_pos
        cx = x * self.cell_size + self.cell_size // 2
        cy = y * self.cell_size + self.cell_size // 2
        r = self.cell_size * 0.35
        self._player_id = self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill="black", outline="white", width=1
        )

    def update_timer(self):
        if not self.game_over and self.moving:
            current_time = time.time()
            self.elapsed_time = current_time - self.start_time
            self.timer_label.config(text=f"Время: {self.elapsed_time:.1f} с")
            self.root.after(100, self.update_timer)

    def end_game(self, win):
        self.game_over = True
        self.moving = False
        final_time = self.elapsed_time
        if win:
            msg = f"Ура, паучок выбрался!\nВремя: {final_time:.2f} секунд"
            title = "Победа!"
        else:
            msg = f"Паучок проиграл((\nПрошло времени: {final_time:.2f} секунд"
            title = "Проигрыш"
        messagebox.showinfo(title, msg)

    def start_dfs(self):
        if self.moving or self.game_over:
            return
        self.moving = True
        self.game_over = False
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.update_timer()
        self.stack = [self.player_pos]
        self.visited = {self.player_pos}
        self.dfs_step()

    def dfs_step(self):
        if self.game_over or not self.moving:
            return
        if not self.stack:
            self.end_game(win=False)
            return

        current = self.stack[-1]
        self.player_pos = current
        self.draw_player()

        x, y = current
        cx = x * self.cell_size + self.cell_size // 2
        cy = y * self.cell_size + self.cell_size // 2
        r = self.cell_size * 0.12
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill="black", outline="", tags="trail"
        )

        if current in self.exit_positions:
            self.end_game(win=True)
            return

        neighbors = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                if not self.maze[ny][nx] and (nx, ny) not in self.visited:
                    neighbors.append((nx, ny))

        if neighbors:
            next_cell = random.choice(neighbors)
            self.visited.add(next_cell)
            self.stack.append(next_cell)
        else:
            self.stack.pop()

        self.root.after(200, self.dfs_step)


if __name__ == "__main__":
    root = tk.Tk()
    game = MazeGame(root, cols=21, rows=15, cell_size=30, num_exits=3)
    root.mainloop()