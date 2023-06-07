import tkinter as tk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Expense import Expense
import database
from functions import get_expenses_by_category
from functions import calculate_category_amount
from functions import calculate_total_amount


class ExpenseTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Expense Tracker")

        # Frame
        self.frame_labels_and_entries = tk.Frame(root, bd=1, relief=tk.SOLID)
        self.frame_labels_and_entries.grid(row=0, column=0, pady=20)

        self.frame_balance = tk.Frame(root, bd=1, relief=tk.SOLID, bg="white")
        self.frame_balance.grid(row=3, column=5, padx=50, sticky="ns")
        for i in range(5):
            self.frame_balance.columnconfigure(i, weight=1)
            self.frame_balance.rowconfigure(i, weight=1)

        self.frame_buttons1 = tk.Frame(root, bd=1, relief=tk.SOLID, bg="white")
        self.frame_buttons1.grid(row=4, column=0, pady=20, padx=35, sticky="w")

        self.frame_expense_per_category_and_month = tk.Frame(root, bd=1, relief=tk.SOLID, bg="white")
        self.frame_expense_per_category_and_month.grid(row=4, column=0, pady=20, padx=35, sticky="e")

        self.frame_buttons2 = tk.Frame(root, bd=1, relief=tk.SOLID, bg="white")
        self.frame_buttons2.grid(row=4, column=5, pady=20, padx=40, sticky="w")
        
        # Labels
        for i, label in enumerate(["Expense Name", "Expense Amount", "Date", "Category", "Month"]):
            tk.Label(self.frame_labels_and_entries, text=label).grid(
                row=0, column=i, pady=5, padx=10)
        
        # Title
        self.title_label = tk.Label(root, text="EXPENSE TRACKER", font=("Open Sans", 24, "bold", "italic")).grid(row=0, column=4, columnspan=2, pady=20, sticky="w")

        # Entries
        self.expense_name_entry = tk.Entry(self.frame_labels_and_entries)
        self.expense_name_entry.grid(row=1, column=0, pady=10, padx=10)

        self.expense_amount_entry = tk.Entry(self.frame_labels_and_entries)
        self.expense_amount_entry.grid(row=1, column=1, pady=10, padx=10)

        self.expense_date_entry = DateEntry(self.frame_labels_and_entries)
        self.expense_date_entry.grid(row=1, column=2, pady=10, padx=10)

        # Comboboxes
        categories = ["All", "Food", "Transportation", "Clothing", "Entertainment", "Other"]
        self.expense_category_menu = ttk.Combobox(self.frame_labels_and_entries, values=categories, state="readonly")
        self.expense_category_menu.grid(row=1, column=3, pady=10, padx=10)
        self.expense_category_menu.bind("<<ComboboxSelected>>", self.load_expenses_to_treeview_by_category)

        months = ["All", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.expense_month_menu = ttk.Combobox(self.frame_labels_and_entries, values=months, state="readonly")
        self.expense_month_menu.grid(row=1, column=4, pady=10, padx=10)
        self.expense_month_menu.bind("<<ComboboxSelected>>", self.load_expenses_to_treeview_by_month)

        # Buttons
        tk.Button(self.frame_buttons1, text="Add", width=15, relief="groove",
                  command=self.add_expense).grid(row=4, column=0, pady=10, padx=10)
        tk.Button(self.frame_buttons1, text="Delete", width=15, relief="groove",
                  command=self.delete_expense).grid(row=5, column=0, pady=10, padx=10)
        tk.Button(self.frame_buttons1, text="Edit", width=15, relief="groove",
                  command=self.edit_expense).grid(row=4, column=1, pady=10, padx=10)
        tk.Button(self.frame_buttons1, text="Clear", width=15, relief="groove",
                  command=self.clear_entries).grid(row=5, column=1, pady=10, padx=10)
        tk.Button(self.frame_buttons2, text="Bar Chart", width=15, relief="groove",
                  command=self.display_bar_chart).grid(row=4, column=2, pady=10, padx=10)
        tk.Button(self.frame_buttons2, text="Pie Chart", width=15, relief="groove",
                  command=self.display_pie_chart).grid(row=5, column=2, pady=10, padx=10)
        tk.Button(self.frame_buttons2, text="Update Income", width=15, relief="groove",
                  command=self.update_income).grid(row=4, column=3, pady=10, padx=10)
        tk.Button(self.frame_buttons2, text="Update Balance", width=15, relief="groove",
                  command=self.update_balance).grid(row=5, column=3, pady=10, padx=10)
        
        self.is_bar_chart_visible = False
        self.is_pie_chart_visible = False
        self.is_balance_visible = False

        # Treeview
        self.expense_treeview = ttk.Treeview(self.master, columns=("id", "name", "amount", "date", "category"), show="headings")
        self.expense_treeview.heading("id", text="No.", command=lambda: self.sort_treeview("id", False))
        self.expense_treeview.heading("name", text="Expense Name", command=lambda: self.sort_treeview("name", False))
        self.expense_treeview.heading("amount", text="Expense Amount", command=lambda: self.sort_treeview("amount", False))
        self.expense_treeview.heading("date", text="Date", command=lambda: self.sort_treeview("date", False))
        self.expense_treeview.heading("category", text="Category", command=lambda: self.sort_treeview("category", False))
        self.expense_treeview.grid(row=3, column=0, columnspan=4, pady=10)
        self.expense_treeview.bind("<<TreeviewSelect>>", self.show_selected_item)
        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.expense_treeview.yview)
        self.expense_treeview.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=3, column=4, sticky="nsw")

        self.expenses = []
        self.total_expense_amount = 0

        self.expense_per_category_label = tk.Label(self.frame_expense_per_category_and_month, text="Expense for Current Category:", font=('Helvetica', 10, 'bold'), bg='white')
        self.expense_per_category_label.grid(row=4, column=1, columnspan=4, pady=10, padx=10)

        self.load_expenses_to_treeview_by_category()

        self.expense_per_month_label = tk.Label(self.frame_expense_per_category_and_month, text=f"Expense for Current Month: ${self.total_expense_amount:.2f}", font=('Helvetica', 10, 'bold'), bg='white')
        self.expense_per_month_label.grid(row=5, column=1, columnspan=4, pady=10, padx=10)

        self.balance = 5000
        self.income = 2000

        # Labels for frame_balance
        self.balance_label = tk.Label(self.frame_balance, text=f"Balance: ${self.balance - self.total_expense_amount:.2f}", font=('Helvetica', 12, 'bold'), bg='white')
        self.balance_label.grid(row=2, column=0, padx=10, pady=10)

        self.balance_after_income_label = tk.Label(self.frame_balance, text=f"Balance Afer Income: ${self.balance - self.total_expense_amount + self.income:.2f}", font=('Helvetica', 12, 'bold'), bg='white')
        self.balance_after_income_label.grid(row=3, column=0, padx=10, pady=10)

        self.income_label = tk.Label(self.frame_balance, text=f"Income: +${self.income:.2f}", font=('Helvetica', 12, 'bold'), bg='white')
        self.income_label.grid(row=0, column=0, padx=10, pady=10)

        self.expense_label = tk.Label(self.frame_balance, text=f"Expenses: -${self.total_expense_amount:.2f}", font=('Helvetica', 12, 'bold'), bg='white')
        self.expense_label.grid(row=1, column=0, padx=10, pady=10)



    def add_expense(self):
        expense_name = self.expense_name_entry.get()
        expense_amount = self.expense_amount_entry.get()
        expense_date = self.expense_date_entry.get()
        expense_category = self.expense_category_menu.get()

        try:
            expense_amount = float(expense_amount)
            if expense_name == "" or expense_amount <= 0 or expense_date == "" or expense_category == "All":
                messagebox.showerror("Error", "Please Enter Valid Inputs")
                return
        except:
            messagebox.showerror("Error", "Please Enter Valid Inputs")
        else:

            self.total_expense_amount += expense_amount

            self.clear_entries()
            self.update_frame_balance()
            expense_id = len(self.expenses) + 1

            expense = Expense(expense_id, expense_name, expense_amount, expense_date, expense_category)
            database.add_expense(expense)

            self.expense_treeview.insert("", "end", values=(
                expense_id, expense_name, expense_amount, expense_date, expense_category))
            self.expenses.append(expense)


    def delete_expense(self):
        selected_item = self.expense_treeview.selection()

        if selected_item:
            selected_item_id = self.expense_treeview.item(selected_item, 'values')[0]
            for expense in self.expenses:
                if expense.id > int(selected_item_id):
                    expense.id -= 1

            self.total_expense_amount -= float(self.expense_treeview.item(selected_item, 'values')[2])

            for item in self.expense_treeview.get_children():
                self.expense_treeview.delete(item)

            database.delete_expense(selected_item_id)

            for expense in self.expenses:
                if expense.id == int(selected_item_id):
                    self.expenses.remove(expense)
                    break

            self.clear_entries()
            self.load_expenses_to_treeview_by_category()
            self.update_frame_balance()
        else:
            messagebox.showerror("Error", "Please select an expense to delete")


    def edit_expense(self):
        selected_item_str = self.expense_treeview.selection()
        if selected_item_str:
            selected_item_id = int(self.expense_treeview.item(
                selected_item_str, 'values')[0])
            selected_item = self.get_expense_by_id(selected_item_id)

            prev_amount = selected_item.amount

            selected_item.name = self.expense_name_entry.get()
            selected_item.amount = float(self.expense_amount_entry.get())
            selected_item.date = self.expense_date_entry.get()
            selected_item.category = self.expense_category_menu.get()

            self.expense_treeview.item(selected_item_str, values=(
                selected_item_id, selected_item.name, selected_item.amount, selected_item.date, selected_item.category))
            
            self.total_expense_amount += selected_item.amount - prev_amount

            expense = Expense(selected_item_id, selected_item.name,
                            selected_item.amount, selected_item.date, selected_item.category)
            database.update_expense(expense)
            self.update_frame_balance()
            self.clear_entries()
        else:
            messagebox.showerror("Error", "Please select an expense to edit")


    def clear_entries(self):
        self.expense_name_entry.delete(0, tk.END)
        self.expense_amount_entry.delete(0, tk.END)
        self.expense_date_entry.delete(0, tk.END)
        self.expense_category_menu.set("")


    def show_selected_item(self, event):
        selected_item = self.expense_treeview.selection()
        
        if selected_item:
            selected_item_id = int(
                self.expense_treeview.item(selected_item, 'values')[0])
            selected_item = self.get_expense_by_id(selected_item_id)

            self.expense_name_entry.delete(0, tk.END)
            self.expense_name_entry.insert(0, selected_item.name)

            self.expense_amount_entry.delete(0, tk.END)
            self.expense_amount_entry.insert(0, selected_item.amount)

            self.expense_date_entry.set_date(selected_item.date)

            self.expense_category_menu.set(selected_item.category)


    def get_expense_by_id(self, id):
        for item in self.expenses:
            if item.id == id:
                return item

    
    def fetch_all_expenses(self):
        if not len(self.expenses):
            self.expenses = database.get_expenses()
            return self.expenses
        else:
            return self.expenses


    def load_expenses_to_treeview_by_category(self, event=None):
        self.fetch_all_expenses()

        for item in self.expense_treeview.get_children():
            self.expense_treeview.delete(item)

        category = self.expense_category_menu.get()

        expenses_by_category = get_expenses_by_category(self.expenses)

        shown_expenses = expenses_by_category.get(category, [])

        amount = 0

        if category == "All" or category == "":
            self.total_expense_amount = calculate_total_amount(self.total_expense_amount, self.expenses)
            amount = self.total_expense_amount
            shown_expenses = self.expenses
        else:
            amount = calculate_category_amount(category, self.expenses)

        self.expense_per_category_label.config(
            text=f"Expense for Current Category: ${amount:.2f}")

        for expense in shown_expenses:
            self.expense_treeview.insert("", "end", values=(
                expense.id, expense.name, expense.amount, expense.date, expense.category))
            

    def load_expenses_to_treeview_by_month(self, event=None):
        self.fetch_all_expenses()

        for item in self.expense_treeview.get_children():
            self.expense_treeview.delete(item)

        month = self.expense_month_menu.get()
        months_dictionary = {"All":"0", "January": "1", "February": "2", "March": "3", "April": "4", "May": "5", "June": "6",
                             "July": "7", "August": "8", "September": "9", "October": "10", "November": "11", "December": "12"}
        
        month_amount = 0

        for expense in self.expenses:
            month_by_number = expense.date.split("/")[0]
            if month_by_number == months_dictionary[month] or month == "All" or month == "":
                month_amount += float(expense.amount)
                self.expense_treeview.insert("", "end", values=(
                    expense.id, expense.name, expense.amount, expense.date, expense.category))
                
        self.expense_per_month_label.config(
            text=f"Expense for Current Month: ${month_amount:.2f}")
        
        
    def sort_treeview(self, column, reverse):
        items = list(self.expense_treeview.get_children())

        if column == "id":
            def key(item): return int(self.expense_treeview.item(item, "values")[0])
        elif column == "name":
            def key(item): return self.expense_treeview.item(item, "values")[1]
        elif column == "amount":
            def key(item): return float(self.expense_treeview.item(item, "values")[2])
        elif column == "date":
            def key(item): return self.expense_treeview.item(item, "values")[3]
        else:
            def key(item): return self.expense_treeview.item(item, "values")[4]

        items.sort(key=key, reverse=reverse)

        for index, item in enumerate(items):
            self.expense_treeview.move(item, "", index)

        self.expense_treeview.heading(column, command=lambda: self.sort_treeview(column, not reverse))


    def display_bar_chart(self):
        if self.is_bar_chart_visible:
            self.bar_window.destroy()
            self.is_bar_chart_visible = False

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        data = [0] * 12
        for expense in self.expenses:
            month_by_number = expense.date.split("/")[0]
            data[int(month_by_number) - 1] += expense.amount

        fig = Figure(figsize=(6, 5), dpi=100)
        fig.add_subplot(111).bar(months, data)

        self.bar_window = tk.Toplevel(self.master, bg="white")
        self.bar_window.title("Bar Chart")
        tk.Label = tk.Label(self.bar_window, text="Expense by Month", bg="white", font=('Helvetica', 14, 'bold')).pack(pady=10)
        canvas = FigureCanvasTkAgg(fig, master=self.bar_window)
        canvas.get_tk_widget().pack()
        canvas.draw()

        self.is_bar_chart_visible = True


    def display_pie_chart(self):
        if self.is_pie_chart_visible:
            self.pie_window.destroy()
            self.is_pie_chart_visible = False

        food_expense_amount = calculate_category_amount("Food", self.expenses)
        transportation_expense_amount = calculate_category_amount(
            "Transportation", self.expenses)
        clothing_expense_amount = calculate_category_amount("Clothing", self.expenses)
        entertainment_expense_amount = calculate_category_amount(
            "Entertainment", self.expenses)
        other_expense_amount = calculate_category_amount("Other", self.expenses)

        data = [food_expense_amount, transportation_expense_amount,
                clothing_expense_amount, entertainment_expense_amount, other_expense_amount]
        labels = ["Food", "Transportation",
                  "Clothing", "Entertainment", "Other"]
        colors = ['yellowgreen', 'gold',
                  'lightskyblue', 'lightcoral', 'orange']

        fig = Figure(figsize=(6, 5), dpi=100)
        fig.add_subplot(111).pie(data, labels=labels,
                                 colors=colors, autopct='%1.1f%%', startangle=90)

        self.pie_window = tk.Toplevel(self.master, bg="white")
        self.pie_window.title("Pie Chart")
        tk.Label = tk.Label(self.pie_window, text="Expense by Category", bg="white", font=('Helvetica', 14, 'bold')).pack(pady=10)
        canvas = FigureCanvasTkAgg(fig, master=self.pie_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.is_pie_chart_visible = True


    def update_frame_balance(self):
        self.income_label.config(
            text=f"Income: +${self.income:.2f}")
        self.balance_label.config(
            text=f"Balance: ${self.balance - self.total_expense_amount:.2f}")
        self.balance_after_income_label.config(
            text=f"Balance Afer Income: ${self.balance - self.total_expense_amount + self.income:.2f}")
        self.expense_label.config(
            text=f"Expenses: -${self.total_expense_amount:.2f}")
        

    def update_income(self):
        def save_income(income_entry):
            try:
                float(income_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid income input")
                return

            self.income = float(income_entry.get())
            self.update_frame_balance()
            self.income_window.destroy()

        self.income_window = tk.Toplevel(self.master)
        self.income_window.geometry("300x100")
        self.income_window.title("Income")

        income_label = tk.Label(self.income_window, text=f"Enter Income: ")
        income_label.pack(pady=5)
        income_entry = tk.Entry(self.income_window)
        income_entry.pack(pady=5)
        income_button = tk.Button(
            self.income_window, text="Save", width=15, relief="groove", command=lambda: save_income(income_entry))
        income_button.pack(pady=5)


    def update_balance(self):
        def save_balance(balance_entry):
            try:
                float(balance_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid balance input")
                return

            self.balance = float(balance_entry.get())
            self.update_frame_balance()
            self.balance_window.destroy()

        self.balance_window = tk.Toplevel(self.master)
        self.balance_window.geometry("300x100")
        self.balance_window.title("Balance")

        balance_label = tk.Label(self.balance_window, text=f"Enter Balance: ")
        balance_label.pack(pady=5)
        balance_entry = tk.Entry(self.balance_window)
        balance_entry.pack(pady=5)
        balance_button = tk.Button(
            self.balance_window, text="Save", width=15, relief="groove", command=lambda: save_balance(balance_entry))
        balance_button.pack(pady=5)


if __name__ == '__main__':
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()