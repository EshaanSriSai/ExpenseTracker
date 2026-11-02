# Expense Tracker

This individual project uses **Python Tkinter** for the graphical form and **SQLite** for database connectivity. It records personal expenses and demonstrates create, read, update, and delete operations.

The interface has a dark green branded header with a custom wallet illustration, colorful spending summary cards, a focused entry form, and softly color-coded transaction rows. Category symbols (such as a bus for Transport and a plate for Food) appear in the picker and table; SQLite still stores the plain category names. The summary updates with the current search results.

## Run the program

1. Install Python 3 if needed.
2. Keep `expense_tracker.py` and this guide together, and keep the included `assets` folder beside them so the header illustration appears.
3. Open a terminal in that folder and run `python expense_tracker.py` (or `py expense_tracker.py` on Windows).
4. The program creates `expenses.db` beside the Python file automatically. Tkinter and SQLite are included with most Python installations; no database server is needed.

## Demonstration steps

1. Add an expense with today's date, a category, a short description, and an amount greater than zero.
2. Show the expense in the table and point out the total of the visible records.
3. Search for a category or a word in a description, then click **Show all** to clear the search.
4. Select a row, change its details, and click **Update selected**.
5. Select a row and click **Delete selected**, then confirm.
6. Close and reopen the app to show that the records remain saved in `expenses.db`.

## How the program works

- Tkinter builds the window, text fields, category menu, buttons, and table.
- `sqlite3` connects Python to the local database file.
- `create_table()` creates the expenses table the first time the program is run.
- Each expense has an automatically generated ID, date, category, description, and amount.
- The Add, Update, Delete, and Search actions run SQL statements.
- SQL `?` placeholders keep entered values separate from the SQL command.
- Database changes are committed using `with connect_db() as connection:`.
- The total is calculated from the records currently displayed; while searching, it totals the matching records.

## Viva practice

1. **What is Tkinter?** Python's standard library for creating graphical user interfaces.
2. **What is SQLite?** A relational database stored in a local file; it does not need a separate server.
3. **What does CRUD stand for?** Create, Read, Update, and Delete—the basic data operations used in the app.
4. **Why does each expense have an ID?** The ID uniquely identifies a row so the program can update or delete the correct expense.
5. **Why use question-mark placeholders in SQL?** They safely pass user values separately from the SQL statement.
6. **What does `mainloop()` do?** It keeps the GUI open and responds to user actions until the window is closed.
7. **How is the total calculated?** The program adds the amount values of the records it has loaded for display.
8. **Where are the records stored?** In `expenses.db`, in the same folder as the Python program.

Practise explaining the functions and demonstrate each feature yourself so you can answer questions about your project.
