import streamlit as st
import pandas as pd


def show_anomaly_detection(df, currency_symbol):

    st.header("Spending Anomaly Detection")

    st.write(
        "Identify unusually high transactions compared with "
        "your normal spending patterns."
    )

    expense_df = df[
        df["Expense/Income"] == "Expense"
    ].copy()

    if expense_df.empty:
        st.warning("No expense transactions available.")
        return

    expense_df["Amount (EUR)"] = pd.to_numeric(
        expense_df["Amount (EUR)"],
        errors="coerce"
    )

    expense_df = expense_df.dropna(
        subset=["Amount (EUR)"]
    )

    if len(expense_df) < 3:
        st.warning(
            "At least three expense transactions are required "
            "for anomaly detection."
        )
        return

    mean_expense = expense_df["Amount (EUR)"].mean()
    std_expense = expense_df["Amount (EUR)"].std()

    # Transactions more than 2 standard deviations
    # above the average are considered unusual.
    threshold = mean_expense + (2 * std_expense)

    anomalies = expense_df[
        expense_df["Amount (EUR)"] > threshold
    ].copy()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Transaction",
        f"{currency_symbol}{mean_expense:.2f}"
    )

    col2.metric(
        "Anomaly Threshold",
        f"{currency_symbol}{threshold:.2f}"
    )

    col3.metric(
        "Anomalies Found",
        len(anomalies)
    )

    st.subheader("Unusual Transactions")

    if anomalies.empty:

        st.success(
            "No unusually high transactions were detected."
        )

    else:

        display_columns = [
            "Date",
            "Name / Description",
            "Category",
            "Amount (EUR)"
        ]

        available_columns = [
            column
            for column in display_columns
            if column in anomalies.columns
        ]

        anomaly_display = anomalies[
            available_columns
        ].copy()

        st.dataframe(
            anomaly_display,
            use_container_width=True
        )

        total_anomaly_amount = anomalies[
            "Amount (EUR)"
        ].sum()

        st.warning(
            f"Detected {len(anomalies)} unusually high "
            f"transactions totaling "
            f"{currency_symbol}{total_anomaly_amount:.2f}."
        )

    st.subheader("Detection Method")

    st.info(
        "A transaction is flagged when its amount is more than "
        "two standard deviations above the average expense "
        "transaction."
    )