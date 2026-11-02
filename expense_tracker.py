"""Expense Tracker: a beginner-friendly Tkinter + SQLite project.

Run with: python expense_tracker.py
The database file (expenses.db) is created beside this script automatically.
"""

import sqlite3
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox, ttk


DB_FILE = Path(__file__).resolve().with_name("expenses.db")
CATEGORY_ICONS = {
    "Food": "🍽", "Transport": "🚌", "Shopping": "🛍",
    "Bills": "💡", "Education": "📚", "Other": "✨",
}
CATEGORY_LABELS = {f"{icon} {name}": name for name, icon in CATEGORY_ICONS.items()}


def connect_db():
    return sqlite3.connect(DB_FILE)


def create_table():
    with connect_db() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS expenses (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   expense_date TEXT NOT NULL,
                   category TEXT NOT NULL,
                   description TEXT NOT NULL,
                   amount REAL NOT NULL CHECK(amount > 0)
               )"""
        )


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1060x720")
        self.root.minsize(900, 630)
        self.root.configure(bg="#f2f5f4")
        self.selected_id = None
        self.search_text = tk.StringVar()
        self.fields = {}

        self.build_screen()
        self.load_expenses()

    def build_screen(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", fieldbackground="white", foreground="#26352f",
                        rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#eef3f0", foreground="#65746d",
                        relief="flat", font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#d9eee5")], foreground=[("selected", "#173c30")])
        style.configure("TEntry", padding=8, font=("Segoe UI", 10))
        style.configure("TCombobox", padding=7, font=("Segoe UI", 10))

        header = tk.Frame(self.root, bg="#173c30", padx=28, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="◈  PENNY TRACK", bg="#173c30", fg="#a5e6c2",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(header, text="Your money, in focus.", bg="#173c30", fg="white",
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(4, 0))
        hero_path = Path(__file__).resolve().parent / "assets" / "penny_track_hero.png"
        try:
            self.hero_image = tk.PhotoImage(file=str(hero_path)).subsample(10, 10)
            tk.Label(header, image=self.hero_image, bg="#173c30").place(relx=1.0, rely=0.5, anchor="e")
        except tk.TclError:
            tk.Label(header, text="PERSONAL FINANCE  •  EXPENSES", bg="#173c30", fg="#c2d6cc",
                     font=("Segoe UI", 9, "bold")).place(relx=1.0, rely=0.72, anchor="e")

        self.total_label = tk.StringVar(value="0.00")
        self.count_label = tk.StringVar(value="0")
        self.category_count_label = tk.StringVar(value="0")
        summary = tk.Frame(self.root, bg="#f2f5f4")
        summary.pack(fill="x", padx=24, pady=(15, 0))
        self.metric_card(summary, "TOTAL SPENDING", self.total_label, "Visible expenses", "#176b49", 0)
        self.metric_card(summary, "TRANSACTIONS", self.count_label, "In this view", "#3156a3", 1)
        self.metric_card(summary, "CATEGORIES", self.category_count_label, "Different types", "#a45c1a", 2)
        for index in range(3):
            summary.columnconfigure(index, weight=1)

        form = tk.LabelFrame(self.root, text="  ADD AN EXPENSE  ", bg="white", fg="#174c3c",
                             padx=16, pady=12, font=("Segoe UI", 11, "bold"))
        form.pack(fill="x", padx=24, pady=(18, 10))

        self.add_field(form, "expense_date", "Date (YYYY-MM-DD)", 0, 0, date.today().isoformat())
        category_box = tk.Frame(form, bg="white")
        category_box.grid(row=0, column=1, sticky="ew", padx=(0, 18), pady=6)
        tk.Label(category_box, text="Category", bg="white", fg="#334155",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        category_choices = tuple(CATEGORY_LABELS)
        category = ttk.Combobox(category_box, values=category_choices)
        category.pack(fill="x", pady=(4, 0), ipady=3)
        self.fields["category"] = category
        self.add_field(form, "description", "Description", 1, 0)
        self.add_field(form, "amount", "Amount", 1, 1)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        actions = tk.Frame(self.root, bg="#f2f5f4")
        actions.pack(fill="x", padx=24, pady=5)
        self.make_button(actions, "＋  Add expense", self.add_expense, "#176b49").pack(side="left", padx=(0, 7))
        self.make_button(actions, "Update selected", self.update_expense, "#3156a3").pack(side="left", padx=7)
        self.make_button(actions, "Delete selected", self.delete_expense, "#bd4c4c").pack(side="left", padx=7)
        self.make_button(actions, "Clear form", self.clear_form, "#67756e").pack(side="left", padx=7)

        search = tk.Frame(self.root, bg="white", padx=15, pady=12)
        search.pack(fill="x", padx=24, pady=(12, 0))
        tk.Label(search, text="Recent expenses", bg="white", fg="#26352f",
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(search, text="Search", bg="white", fg="#829088",
                 font=("Segoe UI", 9, "bold")).pack(side="right")
        search_entry = ttk.Entry(search, textvariable=self.search_text, width=34)
        search_entry.pack(side="right", padx=9, ipady=3)
        search_entry.bind("<KeyRelease>", lambda _event: self.load_expenses())
        self.make_button(search, "Show all", self.show_all, "#67756e").pack(side="right")

        table_frame = tk.Frame(self.root, bg="white", padx=12, pady=8,
                               highlightthickness=1, highlightbackground="#e6ece8")
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 10))
        columns = ("id", "expense_date", "category", "description", "amount")
        labels = {"id": "ID", "expense_date": "Date", "category": "Category",
                  "description": "Description", "amount": "Amount"}
        widths = {"id": 50, "expense_date": 140, "category": 150, "description": 430, "amount": 130}
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            self.table.heading(column, text=labels[column])
            self.table.column(column, width=widths[column], anchor="e" if column == "amount" else "w")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self.select_expense)
        self.category_colors = {
            "food": "#fff1df", "transport": "#e8f2ff", "shopping": "#f4eaff",
            "bills": "#ffeaea", "education": "#e4f6eb", "other": "#eef0f2",
        }
        for category_name, color in self.category_colors.items():
            self.table.tag_configure(f"category_{category_name}", background=color)

        footer = tk.Frame(self.root, bg="#173c30", padx=24, pady=9)
        footer.pack(fill="x", side="bottom")
        self.status = tk.StringVar(value="Ready")
        tk.Label(footer, textvariable=self.status, bg="#173c30", fg="#d1e3d9",
                 font=("Segoe UI", 9)).pack(side="left")
        tk.Label(footer, text="PENNY TRACK  •  SQLITE DATABASE", bg="#173c30", fg="#91b6a3",
                 font=("Segoe UI", 8, "bold")).pack(side="right")

    @staticmethod
    def metric_card(parent, title, value, hint, accent, column):
        card = tk.Frame(parent, bg="white", padx=15, pady=10,
                        highlightthickness=1, highlightbackground="#e6ece8")
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 7, 0 if column == 2 else 7))
        tk.Label(card, text=title, bg="white", fg="#829088",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(card, textvariable=value, bg="white", fg=accent,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(card, text=hint, bg="white", fg="#829088",
                 font=("Segoe UI", 8)).pack(anchor="w")

    def add_field(self, parent, key, label, row, column, value=""):
        box = tk.Frame(parent, bg="white")
        box.grid(row=row, column=column, sticky="ew", padx=(0, 18), pady=6)
        tk.Label(box, text=label.upper(), bg="white", fg="#65746d",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        entry = ttk.Entry(box, font=("Segoe UI", 10))
        entry.pack(fill="x", pady=(4, 0), ipady=4)
        if value:
            entry.insert(0, value)
        self.fields[key] = entry

    @staticmethod
    def make_button(parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bg=color, fg="white",
                         activebackground=color, activeforeground="white", relief="flat",
                         padx=14, pady=8, cursor="hand2", font=("Segoe UI", 9, "bold"),
                         borderwidth=0, highlightthickness=0)

    def form_values(self):
        values = {key: field.get().strip() for key, field in self.fields.items()}
        try:
            parsed_date = date.fromisoformat(values["expense_date"])
        except ValueError:
            messagebox.showwarning("Check the date", "Enter a valid date in YYYY-MM-DD format, for example 2026-11-02.")
            return None
        if not values["category"] or not values["description"]:
            messagebox.showwarning("Missing information", "Please enter a category and description.")
            return None
        values["category"] = CATEGORY_LABELS.get(values["category"], values["category"])
        try:
            amount = float(values["amount"])
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Check the amount", "Enter an amount greater than zero, such as 120 or 45.50.")
            return None
        values["expense_date"] = parsed_date.isoformat()
        values["amount"] = amount
        return values

    def add_expense(self):
        values = self.form_values()
        if values is None:
            return
        with connect_db() as connection:
            connection.execute(
                "INSERT INTO expenses (expense_date, category, description, amount) VALUES (?, ?, ?, ?)",
                (values["expense_date"], values["category"], values["description"], values["amount"]),
            )
        self.clear_form()
        self.load_expenses()
        self.status.set("Expense added.")

    def update_expense(self):
        if self.selected_id is None:
            messagebox.showinfo("Select an expense", "Click an expense row first, then choose Update selected.")
            return
        values = self.form_values()
        if values is None:
            return
        with connect_db() as connection:
            connection.execute(
                "UPDATE expenses SET expense_date=?, category=?, description=?, amount=? WHERE id=?",
                (values["expense_date"], values["category"], values["description"], values["amount"], self.selected_id),
            )
        self.clear_form()
        self.load_expenses()
        self.status.set("Expense updated.")

    def delete_expense(self):
        if self.selected_id is None:
            messagebox.showinfo("Select an expense", "Click an expense row first, then choose Delete selected.")
            return
        if not messagebox.askyesno("Confirm deletion", "Delete the selected expense?"):
            return
        with connect_db() as connection:
            connection.execute("DELETE FROM expenses WHERE id=?", (self.selected_id,))
        self.clear_form()
        self.load_expenses()
        self.status.set("Expense deleted.")

    def load_expenses(self):
        for item in self.table.get_children():
            self.table.delete(item)
        term = self.search_text.get().strip()
        with connect_db() as connection:
            if term:
                rows = connection.execute(
                    "SELECT id, expense_date, category, description, amount FROM expenses "
                    "WHERE category LIKE ? OR description LIKE ? ORDER BY expense_date DESC, id DESC",
                    (f"%{term}%", f"%{term}%"),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT id, expense_date, category, description, amount FROM expenses "
                    "ORDER BY expense_date DESC, id DESC"
                ).fetchall()
        for row in rows:
            tag = f"category_{str(row[2]).casefold()}"
            tags = (tag,) if str(row[2]).casefold() in self.category_colors else ()
            category_display = f"{CATEGORY_ICONS.get(row[2], '🔹')}  {row[2]}"
            self.table.insert("", "end", values=(row[0], row[1], category_display, row[3], f"{row[4]:.2f}"), tags=tags)
        visible_total = sum(float(row[4]) for row in rows)
        self.total_label.set(f"{visible_total:.2f}")
        self.count_label.set(str(len(rows)))
        self.category_count_label.set(str(len({row[2] for row in rows})))
        self.status.set(f"Showing {len(rows)} expense(s).")

    def select_expense(self, _event=None):
        selection = self.table.selection()
        if not selection:
            return
        values = self.table.item(selection[0], "values")
        self.selected_id = int(values[0])
        for key, value in zip(("expense_date", "category", "description", "amount"), values[1:]):
            self.fields[key].delete(0, tk.END)
            if key == "category":
                category_name = value.split("  ", 1)[-1].strip()
                value = f"{CATEGORY_ICONS.get(category_name, '🔹')} {category_name}"
            self.fields[key].insert(0, value)
        self.status.set(f"Selected expense ID {self.selected_id}.")

    def clear_form(self):
        for field in self.fields.values():
            field.delete(0, tk.END)
        self.fields["expense_date"].insert(0, date.today().isoformat())
        self.selected_id = None
        for selected in self.table.selection():
            self.table.selection_remove(selected)

    def show_all(self):
        self.search_text.set("")
        self.load_expenses()


if __name__ == "__main__":
    create_table()
    window = tk.Tk()
    app = ExpenseTracker(window)
    window.mainloop()
