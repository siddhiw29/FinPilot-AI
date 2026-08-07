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