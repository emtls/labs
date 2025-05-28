import tkinter as tk
from tkinter import messagebox
from itertools import product

#Функция распределения предметов между людьми
def assign_items_to_people(item_ids, distribution):
    num_people = max(distribution) + 1
    people = [[] for _ in range(num_people)]
    for item_id, person_idx in zip(item_ids, distribution):
        people[person_idx].append(item_id)
    return [sorted(group) for group in people]

def find_optimal_distribution(total_items, total_people, min_items=1, max_items=2):
    all_distributions = set()
    roughness_list = []

    item_ids = list(range(1, total_items + 1))

    for pattern in product(range(total_people), repeat=total_items):
        used_people = set(pattern)
        if len(used_people) < total_people:
            continue

        dist = assign_items_to_people(item_ids, pattern)

        counts = [len(g) for g in dist]
        if min(counts) < min_items or max(counts) > max_items:
            continue

        key = tuple(tuple(group) for group in dist)
        if key in all_distributions:
            continue
        all_distributions.add(key)

        rough = max(counts) - min(counts)
        roughness_list.append((dist, rough))

    if not roughness_list:
        return None, 0

    min_rough = min(r[1] for r in roughness_list)
    best_options = [r for r in roughness_list if r[1] == min_rough]

    return best_options[0], len(all_distributions)

#графический интерфейс
class ItemDistributionApp:
    def __init__(self, root):
        self.root = root
        root.title("Распределение предметов между людьми")
        root.geometry("600x500")

        tk.Label(root, text="Количество предметов:", font=("Arial", 12)).pack(pady=5)
        self.items_entry = tk.Entry(root, font=("Arial", 12))
        self.items_entry.pack()

        tk.Label(root, text="Количество людей:", font=("Arial", 12)).pack(pady=5)
        self.people_entry = tk.Entry(root, font=("Arial", 12))
        self.people_entry.pack()

        tk.Label(root, text="Минимальное количество предметов:", font=("Arial", 12)).pack(pady=5)
        self.min_items_entry = tk.Entry(root, font=("Arial", 12))
        self.min_items_entry.insert(0, "1")
        self.min_items_entry.pack()

        tk.Label(root, text="Максимальное количество предметов:", font=("Arial", 12)).pack(pady=5)
        self.max_items_entry = tk.Entry(root, font=("Arial", 12))
        self.max_items_entry.insert(0, "2")
        self.max_items_entry.pack()

        # Кнопка
        self.run_button = tk.Button(root, text="Найти оптимальное распределение",
                                  command=self.run_calculation, font=("Arial", 12))
        self.run_button.pack(pady=10)

        # Выходной текст
        self.output_frame = tk.Frame(root)
        self.output_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.output_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD,
                                 yscrollcommand=self.scrollbar.set, font=("Courier", 12))
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.output_text.yview)

    def run_calculation(self):
        try:
            total_items = int(self.items_entry.get())
            total_people = int(self.people_entry.get())
            min_items = int(self.min_items_entry.get())
            max_items = int(self.max_items_entry.get())

            if total_items <= 0 or total_people <= 0:
                raise ValueError("Число должно быть положительным.")
            if min_items > max_items:
                raise ValueError("Минимальное количество не может быть больше максимального.")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        result = find_optimal_distribution(total_items, total_people, min_items, max_items)

        self.output_text.delete('1.0', tk.END)

        if result == (None, 0):
            self.output_text.insert(tk.END, "Не найдено допустимых распределений.\n")
        else:
            (best_dist, roughness), total_dists = result
            output = f"Оптимальное распределение предметов:\n"
            for i, items in enumerate(best_dist):
                output += f"  Человек {i+1}: {items}\n"
            output += f"\nРазница в количестве предметов: {roughness}\n"
            output += f"Всего допустимых распределений: {total_dists}\n"

            self.output_text.insert(tk.END, output)
root = tk.Tk()
app = ItemDistributionApp(root)
root.mainloop()