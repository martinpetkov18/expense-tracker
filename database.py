import sqlite3
from Expense import Expense

conn = sqlite3.connect('expenses.db')

conn.execute("DROP TABLE IF EXISTS expenses")

conn.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             amount REAL NOT NULL,
             date TEXT NOT NULL,
             category TEXT NOT NULL);''')



def add_expense(expense: Expense):
    conn = sqlite3.connect('expenses.db')
    conn.execute("INSERT INTO expenses (name, amount, date, category) VALUES (?, ?, ?, ?)",
                 (expense.name, expense.amount, expense.date, expense.category))
    conn.commit()
    conn.close()

expenses = [
    Expense(id=1, name="Coffee", amount=2.50, date="4/1/2023", category="Food"),
    Expense(id=2, name="Gas", amount=35.75, date="6/2/2023", category="Transportation"),
    Expense(id=3, name="Movie tickets", amount=18.00, date="7/3/2023", category="Entertainment"),
    Expense(id=4, name="Groceries", amount=65.20, date="8/4/2023", category="Food"),
    Expense(id=5, name="Gym membership", amount=50.00, date="4/5/2023", category="Other"),
    Expense(id=6, name="Books", amount=27.95, date="9/6/2023", category="Entertainment"),
    Expense(id=7, name="Haircut", amount=25.00, date="10/7/2023", category="Other"),
    Expense(id=8, name="Phone bill", amount=85.00, date="11/8/2023", category="Other"),
    Expense(id=9, name="Clothes", amount=120.00, date="12/9/2023", category="Clothing"),
    Expense(id=10, name="Dinner", amount=45.00, date="1/10/2023", category="Food"),
    Expense(id=11, name="Electricity bill", amount=80.00, date="2/1/2023", category="Other"),
    Expense(id=12, name="Concert tickets", amount=75.00, date="3/2/2023", category="Entertainment"),
    Expense(id=13, name="Lunch", amount=12.50, date="5/3/2023", category="Food"),
    Expense(id=14, name="Car repair", amount=250.00, date="5/4/2023", category="Transportation"),
    Expense(id=15, name="Netflix subscription", amount=14.99, date="5/5/2023", category="Entertainment"),
    Expense(id=16, name="Office supplies", amount=45.00, date="4/6/2023", category="Other"),
    Expense(id=17, name="Dentist appointment", amount=150.00, date="7/7/2023", category="Other"),
    Expense(id=18, name="Groceries", amount=80.00, date="7/8/2023", category="Food"),
    Expense(id=19, name="Movie rental", amount=5.99, date="6/15/2023", category="Entertainment"),
    Expense(id=20, name="Gas", amount=40.25, date="6/20/2023", category="Transportation")
]

for expense in expenses:
    add_expense(expense)

def get_expenses():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.execute(
        "SELECT id, name, amount, date, category FROM expenses")
    expenses = []
    for row in cursor:
        expense = Expense(row[0], row[1], row[2], row[3], row[4])
        expenses.append(expense)
    conn.close()
    return expenses

def update_expense(expense):
    conn = sqlite3.connect('expenses.db')
    conn.execute("UPDATE expenses SET name = ?, amount = ?, date = ?, category = ? WHERE id = ?",
                 (expense.name, expense.amount, expense.date, expense.category, expense.id))
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = sqlite3.connect('expenses.db')
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def get_expense_by_id(expense_id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, amount, date, category FROM expenses WHERE id=?", (expense_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    expense = Expense(row[0], row[1], row[2], row[3], row[4])
    conn.close()
    return expense