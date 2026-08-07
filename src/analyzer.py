import pandas as pd


def calculate_summary(df):
    """
    Calculate income, expense and savings.
    """

    income = df[df["Expense/Income"] == "Income"]["Amount (EUR)"].sum()

    expense = df[df["Expense/Income"] == "Expense"]["Amount (EUR)"].sum()

    savings = income - expense

    return income, expense, savings


def category_summary(df):
    """
    Calculate spending by category.
    """

    expense_df = df[df["Expense/Income"] == "Expense"]

    return (
        expense_df.groupby("Category")["Amount (EUR)"]
        .sum()
        .sort_values(ascending=False)
    )
def financial_health_score(income, expense, savings):
    """
    Returns a financial health score out of 100.
    """

    if income == 0:
        return 0

    savings_rate = (savings / income) * 100

    score = 0

    # Savings Rate (60 marks)
    if savings_rate >= 50:
        score += 60
    elif savings_rate >= 30:
        score += 45
    elif savings_rate >= 15:
        score += 30
    else:
        score += 15

    # Expense Ratio (40 marks)
    expense_ratio = (expense / income) * 100

    if expense_ratio <= 40:
        score += 40
    elif expense_ratio <= 60:
        score += 30
    elif expense_ratio <= 80:
        score += 20
    else:
        score += 10

    return min(score, 100)