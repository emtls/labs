import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

PALETTE_BG = "#eef3f7"
PALETTE_CANVAS = "#f9fbfc"
PALETTE_TEXT = "#243447"
PALETTE_ACCENT = "#7fc8a9"
PALETTE_ACCENT_DARK = "#65b698"
PALETTE_HILITE = "#cfeee3"

class Contract:
    def __init__(self, sid: str, htype: str, manager: str, amount: float):
        self.sid = sid
        self.htype = htype
        self.manager = manager
        self.amount = float(amount)

    @staticmethod
    def from_list(row):
        if len(row) != 4:
            raise ValueError("ожидалось 4 поля (id,type,manager,amount)")
        sid, htype, manager, amount = row
        sid = str(sid).strip()
        htype = str(htype).strip()
        manager = str(manager).strip()
        if not sid or not htype or not manager:
            raise ValueError("id/type/manager пусты")
        try:
            amount = float(amount)
        except Exception:
            raise ValueError("amount должен быть числом")
        if amount < 0:
            raise ValueError("amount должен быть >= 0")
        return Contract(sid, htype, manager, amount)

    def is_type(self, kind: str):
        return self.htype.lower() == str(kind).lower()

    def is_manager(self, name: str):
        return self.manager.lower() == str(name).lower()

    def as_row(self):
        return [self.sid, self.htype, self.manager, f"{self.amount:.2f}"]


class ContractsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Договоры на продажу жилья")
        self.contracts = []
        self._setup_style()
        self.build_gui()

    def _setup_style(self):
        self.root.configure(bg=PALETTE_BG)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Calm.TFrame", background=PALETTE_BG)
        style.configure("Calm.TLabel", background=PALETTE_BG, foreground=PALETTE_TEXT, font=("Segoe UI", 10))
        style.configure("Calm.TButton",
                        background=PALETTE_ACCENT,
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        padding=6)
        style.map("Calm.TButton",
                  background=[("active", PALETTE_ACCENT_DARK)],
                  relief=[("pressed", "sunken"), ("!pressed", "raised")])

        style.configure("Calm.Treeview",
                        background=PALETTE_CANVAS,
                        foreground=PALETTE_TEXT,
                        fieldbackground=PALETTE_CANVAS,
                        rowheight=26,
                        borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Calm.Treeview.Heading",
                        background=PALETTE_BG,
                        foreground=PALETTE_TEXT,
                        font=("Segoe UI", 10, "bold"))
        style.map("Calm.Treeview",
                  background=[("selected", PALETTE_HILITE)],
                  foreground=[("selected", PALETTE_TEXT)])

    def build_gui(self):
        top = ttk.Frame(self.root, style="Calm.TFrame")
        top.pack(padx=14, pady=12, fill='x')

        ttk.Button(top, text="Загрузить CSV", style="Calm.TButton", command=self.load_csv).grid(row=0, column=0, padx=6)
        ttk.Button(top, text="Сохранить CSV", style="Calm.TButton", command=self.save_csv).grid(row=0, column=1, padx=6)
        ttk.Button(top, text="Диаграмма по видам жилья", style="Calm.TButton", command=self.show_pie_by_type).grid(
            row=0, column=2, padx=6)
        ttk.Button(top, text="Диаграмма по менеджерам", style="Calm.TButton", command=self.show_pie_by_manager).grid(
            row=0, column=3, padx=6)

        tf = ttk.Frame(self.root, style="Calm.TFrame")
        tf.pack(padx=14, fill='both')
        self.tree = ttk.Treeview(tf, columns=("ID", "Type", "Manager", "Amount"),
                                 show='headings', height=12, style="Calm.Treeview")
        for col, w in [("ID", 120), ("Type", 200), ("Manager", 200), ("Amount", 140)]:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=w, anchor='center')
        sb = ttk.Scrollbar(tf, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='left', fill='y', padx=(0, 6))
        self.tree.bind('<Double-1>', self.on_double_click)

        self.canvas = tk.Canvas(self.root, width=900, height=560, bg=PALETTE_CANVAS, highlightthickness=0)
        self.canvas.pack(padx=14, pady=12)

    def parse_csv_line(self, line):
        line = line.strip()
        if not line:
            return []

        fields = []
        field = ""
        in_quotes = False
        i = 0

        while i < len(line):
            char = line[i]

            if char == '"':
                if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                    field += '"'
                    i += 1
                else:
                    in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                fields.append(field)
                field = ""
            else:
                field += char
            i += 1

        fields.append(field)
        return [field.strip('"') for field in fields]

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
        if not path:
            return
        goods, bads = [], []
        try:
            with open(path, encoding='utf-8') as f:
                header_checked = False
                for nr, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue

                    row = self.parse_csv_line(line)

                    if not header_checked:
                        header_checked = True
                        if row and row[0].lower() == "id":
                            continue

                    try:
                        c = Contract.from_list(row)
                        goods.append(c)
                    except Exception as e:
                        bads.append((nr, row, str(e)))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка чтения файла: {str(e)}")
            return

        self.contracts = goods
        self.refresh_tree()
        if bads:
            messagebox.showwarning("Готово", f"Загружено: {len(goods)}, Пропущено строк: {len(bads)}")
        else:
            messagebox.showinfo("Готово", f"Успешно загружено {len(goods)} записей")

    def save_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("id,type,manager,amount\n")
                for c in self.contracts:
                    row = []
                    for field in [c.sid, c.htype, c.manager, f"{c.amount:.2f}"]:
                        if ',' in field or '"' in field:
                            field = field.replace('"', '""')
                            field = f'"{field}"'
                        row.append(field)
                    f.write(','.join(row) + '\n')
            messagebox.showinfo("Готово", "Файл успешно сохранён.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

    def refresh_tree(self, data=None):
        data = self.contracts if data is None else data
        self.tree.delete(*self.tree.get_children())
        for c in data:
            self.tree.insert('', 'end', values=(c.sid, c.htype, c.manager, f"{c.amount:,.0f}"))

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item or not col:
            return
        idx = self.tree.index(item)
        ci = int(col.replace('#', '')) - 1
        c = self.contracts[idx]
        old = self.tree.item(item, 'values')[ci]
        if ci == 1:
            new = simpledialog.askstring("Тип жилья", "Новый тип:", initialvalue=c.htype)
            if new:
                c.htype = new.strip()
        elif ci == 2:
            new = simpledialog.askstring("Менеджер", "Новое имя:", initialvalue=c.manager)
            if new:
                c.manager = new.strip()
        elif ci == 3:
            new = simpledialog.askfloat("Сумма", "Новая сумма:", initialvalue=float(c.amount))
            if new is not None and new >= 0:
                c.amount = float(new)
        else:
            new = simpledialog.askstring("ID", "Новый ID:", initialvalue=c.sid)
            if new:
                c.sid = new.strip()
        self.refresh_tree()

    def segment_by_type(self):
        stats = {}
        for c in self.contracts:
            stats[c.htype] = stats.get(c.htype, 0) + 1
        return stats

    def segment_by_manager(self):
        stats = {}
        for c in self.contracts:
            stats[c.manager] = stats.get(c.manager, 0) + 1
        return stats

    def show_pie(self, counts: dict, title: str):
        self.canvas.delete('all')
        total = sum(counts.values())
        if total == 0:
            self.canvas.create_text(450, 280, text="Нет данных для отображения",
                                    font=("Segoe UI", 14), fill=PALETTE_TEXT)
            return

        cx, cy = 450, 280
        r = 220
        self.canvas.create_text(cx, 40, text=title, font=("Segoe UI", 16, "bold"), fill=PALETTE_TEXT)
        palette = ["#81c784", "#64b5f6", "#e57373", "#ffd54f", "#ba68c8", "#4db6ac", "#ff8a65"]
        start = 0
        items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        for i, (label, cnt) in enumerate(items):
            extent = 360 * cnt / total
            arc = self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                         start=start, extent=extent,
                                         fill=palette[i % len(palette)],
                                         outline=PALETTE_CANVAS, width=2)
            self.canvas.tag_bind(arc, '<Button-1>',
                                 lambda e, l=label, c=cnt: messagebox.showinfo('Сегмент',
                                                                               f"{l}: {c} ({c / total * 100:.1f}%)"))
            start += extent
        lx, ly = cx + r + 30, cy - r
        for i, (label, cnt) in enumerate(items):
            y = ly + i * 26
            self.canvas.create_rectangle(lx, y, lx + 18, y + 14,
                                         fill=palette[i % len(palette)], outline='#dde7ec')
            self.canvas.create_text(lx + 24, y + 7, text=f"{label}: {cnt} ({cnt / total * 100:.1f}%)",
                                    anchor='w', font=("Segoe UI", 11), fill=PALETTE_TEXT)

    def show_pie_by_type(self):
        self.show_pie(self.segment_by_type(), "Сегментация по видам жилья")

    def show_pie_by_manager(self):
        self.show_pie(self.segment_by_manager(), "Сегментация по менеджерам")

if __name__ == "__main__":
    root = tk.Tk()
    app = ContractsApp(root)
    root.mainloop()