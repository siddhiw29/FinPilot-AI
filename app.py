import pandas as pd

from src.categorizer import assign_category
from src.analyzer import calculate_summary, category_summary
from src.recommendations import generate_recommendations


def main():

    print("=" * 50)
    print(" FinPilot AI")
    print("=" * 50)

    df = pd.read_csv("data/transactions_2022_2023.csv")

    df["Category"] = df["Name / Description"].apply(assign_category)

    income, expense, savings = calculate_summary(df)

    category_spending = category_summary(df)

    print(f"\nIncome   : €{income:.2f}")
    print(f"Expense  : €{expense:.2f}")
    print(f"Savings  : €{savings:.2f}")

    print("\nTop Spending Categories")
    print(category_spending.head())

    print("\nAI Recommendations")
    print("-" * 40)

    recommendations = generate_recommendations(
        savings,
        category_spending
    )

    for recommendation in recommendations:
        print(recommendation)


if __name__ == "__main__":
    main()