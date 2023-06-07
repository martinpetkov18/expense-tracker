def get_expenses_by_category(expenses):
  expenses_by_category = {}
  for expense in expenses:
      category = expense.category
      if category not in expenses_by_category:
          expenses_by_category[category] = []
      expenses_by_category[category].append(expense)
  return expenses_by_category


def calculate_category_amount(category, expenses):
    category_amount = 0

    expenses_by_category = get_expenses_by_category(expenses)

    expenses = expenses_by_category.get(category, [])

    for item in expenses:
        category_amount += float(item.amount)

    return category_amount

def calculate_total_amount(total_expense_amount, expenses):
    if total_expense_amount:
        return total_expense_amount
    else:
        for item in expenses:
            total_expense_amount += float(item.amount)
        return total_expense_amount