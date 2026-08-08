import pandas as pd


def generate_financial_report(
    df,
    income,
    expense,
    savings,
    currency_symbol
):
    report = []

    savings_rate = (
        (savings / income) * 100
        if income > 0
        else 0
    )

    report.append("FINPILOT AI - FINANCIAL REPORT")
    report.append("=" * 40)
    report.append("")

    report.append(
        f"Total Income: {currency_symbol}{income:.2f}"
    )

    report.append(
        f"Total Expense: {currency_symbol}{expense:.2f}"
    )

    report.append(
        f"Total Savings: {currency_symbol}{savings:.2f}"
    )

    report.append(
        f"Savings Rate: {savings_rate:.1f}%"
    )

    report.append("")
    report.append("TOP SPENDING CATEGORIES")
    report.append("-" * 40)

    category_spending = (
        df[df["Expense/Income"] == "Expense"]
        .groupby("Category")["Amount (EUR)"]
        .sum()
        .sort_values(ascending=False)
    )

    for category, amount in category_spending.items():

        report.append(
            f"{category}: "
            f"{currency_symbol}{amount:.2f}"
        )

    report.append("")
    report.append("=" * 40)
    report.append("Generated using FinPilot AI")

    return "\n".join(report)