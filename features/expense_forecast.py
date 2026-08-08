import streamlit as st
import pandas as pd
import numpy as np


def show_expense_forecast(df, currency_symbol):

    st.header("Expense Forecast")

    st.write(
        "Estimate next month's expenses using your historical "
        "monthly spending patterns."
    )

    expense_df = df[
        df["Expense/Income"] == "Expense"
    ].copy()

    if expense_df.empty:
        st.warning("No expense data available for forecasting.")
        return

    expense_df["Date"] = pd.to_datetime(
        expense_df["Date"]
    )

    monthly = (
        expense_df
        .groupby(
            expense_df["Date"].dt.to_period("M")
        )["Amount (EUR)"]
        .sum()
        .reset_index()
    )

    monthly["Date"] = monthly["Date"].astype(str)

    if len(monthly) < 2:
        st.warning(
            "At least two months of expense data are required "
            "for forecasting."
        )
        return

    values = monthly["Amount (EUR)"].values

    # Simple linear trend forecasting
    x = np.arange(len(values))

    slope, intercept = np.polyfit(
        x,
        values,
        1
    )

    next_month_index = len(values)

    predicted_expense = (
        slope * next_month_index + intercept
    )

    predicted_expense = max(
        predicted_expense,
        0
    )

    average_expense = values.mean()

    # Determine spending trend
    if slope > 0:
        trend = "Increasing"
    elif slope < 0:
        trend = "Decreasing"
    else:
        trend = "Stable"

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Monthly Expense",
        f"{currency_symbol}{average_expense:.2f}"
    )

    col2.metric(
        "Predicted Next Month",
        f"{currency_symbol}{predicted_expense:.2f}"
    )

    col3.metric(
        "Spending Trend",
        trend
    )

    st.subheader("Historical Expenses")

    chart_df = monthly.copy()

    chart_df["Amount (EUR)"] = chart_df[
        "Amount (EUR)"
    ]

    st.line_chart(
        chart_df.set_index("Date")[
            "Amount (EUR)"
        ]
    )

    st.subheader("Forecast Summary")

    if trend == "Increasing":
        st.warning(
            "Your expenses show an increasing trend. "
            "Consider reviewing your highest spending categories."
        )

    elif trend == "Decreasing":
        st.success(
            "Your expenses show a decreasing trend. "
            "Keep maintaining your current spending habits."
        )

    else:
        st.info(
            "Your expenses are relatively stable."
        )

    st.caption(
        "Forecast is based on a linear trend from historical "
        "monthly expenses and should be treated as an estimate."
    )