import streamlit as st
import pandas as pd


def show_budget_planner(df, currency_symbol):

    st.header("Monthly Budget Planner")

    st.write(
        "Set spending limits for your expense categories "
        "and track your spending."
    )

    expense_df = df[
        df["Expense/Income"] == "Expense"
    ].copy()

    categories = sorted(
        expense_df["Category"].dropna().unique()
    )

    if not categories:
        st.warning("No expense categories found.")
        return

    budget_data = []

    for category in categories:

        spent = expense_df[
            expense_df["Category"] == category
        ]["Amount (EUR)"].sum()

        budget = st.number_input(
            f"Budget for {category}",
            min_value=0.0,
            value=500.0,
            step=50.0,
            key=f"budget_{category}"
        )

        remaining = budget - spent

        if remaining >= 0:
            status = "Under Budget"
        else:
            status = "Over Budget"

        budget_data.append({
            "Category": category,
            "Budget": budget,
            "Spent": spent,
            "Remaining": remaining,
            "Status": status
        })

    budget_df = pd.DataFrame(budget_data)

    st.subheader("Budget Summary")

    total_budget = budget_df["Budget"].sum()
    total_spent = budget_df["Spent"].sum()
    total_remaining = total_budget - total_spent

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Budget",
        f"{currency_symbol}{total_budget:.2f}"
    )

    col2.metric(
        "Total Spent",
        f"{currency_symbol}{total_spent:.2f}"
    )

    col3.metric(
        "Remaining",
        f"{currency_symbol}{total_remaining:.2f}"
    )

    st.dataframe(
        budget_df,
        use_container_width=True
    )

    st.subheader("Budget Status")

    for _, row in budget_df.iterrows():

        if row["Remaining"] >= 0:

            st.success(
                f"{row['Category']}: "
                f"{currency_symbol}{row['Remaining']:.2f} remaining"
            )

        else:

            st.error(
                f"{row['Category']}: "
                f"{currency_symbol}{abs(row['Remaining']):.2f} over budget"
            )