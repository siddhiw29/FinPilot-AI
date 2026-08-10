import re

import streamlit as st
import pandas as pd
import plotly.express as px

from src.categorizer import assign_category
from src.analyzer import (
    calculate_summary,
    financial_health_score,
)

from features.auth import show_auth
from src.supabase_client import get_supabase

from features.currency import (
    convert_dataframe,
    get_currency_symbol,
)

from features.savings_goal import show_savings_goal
from features.budget_planner import show_budget_planner
from features.report_generator import generate_financial_report
from features.expense_forecast import show_expense_forecast
from features.anomaly_detection import show_anomaly_detection
from features.ai_chat import show_ai_chat


# ====================================================
# PAGE CONFIGURATION
# ====================================================

st.set_page_config(
    page_title="FinPilot AI",
    layout="wide"
)


# ====================================================
# AUTHENTICATION
# ====================================================

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    show_auth()
    st.stop()


# ====================================================
# HELPER FUNCTIONS
# ====================================================

def detect_currency(df):
    """
    Automatically detect the original currency of a CSV.

    Detection order:
    1. Currency / Currency Code columns
    2. Amount column names such as Amount (INR)
    3. Currency symbols inside amount values

    Returns:
        INR / USD / EUR / GBP
        or None if currency cannot be detected.
    """

    supported = ["INR", "USD", "EUR", "GBP"]

    # -----------------------------------------------
    # 1. Look for Currency / Currency Code columns
    # -----------------------------------------------

    currency_columns = [
        col for col in df.columns
        if str(col).strip().lower()
        in ["currency", "currency code", "currency_code"]
    ]

    for col in currency_columns:

        values = (
            df[col]
            .dropna()
            .astype(str)
            .str.upper()
            .str.strip()
        )

        for value in values:

            for currency in supported:

                if currency == value:
                    return currency

                if currency in value:
                    return currency

    # -----------------------------------------------
    # 2. Look at column names
    # -----------------------------------------------

    for column in df.columns:

        column_text = str(column).upper()

        for currency in supported:

            if currency in column_text:
                return currency

    # -----------------------------------------------
    # 3. Look for currency symbols in values
    # -----------------------------------------------

    for column in df.columns:

        values = df[column].dropna().astype(str)

        for value in values.head(50):

            if "₹" in value or "RS." in value.upper() or "INR" in value.upper():
                return "INR"

            if "€" in value or "EUR" in value.upper():
                return "EUR"

            if "£" in value or "GBP" in value.upper():
                return "GBP"

            if "$" in value or "USD" in value.upper():
                return "USD"

    return None


def find_amount_column(df):
    """
    Find the transaction amount column.
    """

    # First look for common exact names
    preferred_names = [
        "Amount",
        "Amount (EUR)",
        "Amount (INR)",
        "Amount (USD)",
        "Amount (GBP)",
        "Transaction Amount",
        "Transaction_Amount",
    ]

    for name in preferred_names:

        if name in df.columns:
            return name

    # Otherwise find a column containing 'amount'
    for column in df.columns:

        if "amount" in str(column).lower():
            return column

    return None


def clean_amount(value):
    """
    Convert amount values containing currency symbols,
    commas, spaces, etc. into a float.
    """

    if pd.isna(value):
        return 0.0

    value = str(value).strip()

    # Remove common currency symbols
    value = (
        value
        .replace("₹", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .replace("INR", "")
        .replace("USD", "")
        .replace("EUR", "")
        .replace("GBP", "")
        .replace(",", "")
        .strip()
    )

    return float(value)


def prepare_dataframe(df):
    """
    Normalize uploaded CSV into the column structure
    expected by the rest of FinPilot.
    """

    df = df.copy()

    # -----------------------------------------------
    # Amount
    # -----------------------------------------------

    amount_column = find_amount_column(df)

    if amount_column is None:
        raise ValueError(
            "Could not find an amount column in the CSV. "
            "Please make sure your file contains a column "
            "such as Amount or Amount (INR)."
        )

    df["Amount (EUR)"] = df[amount_column].apply(clean_amount)

    # -----------------------------------------------
    # Description
    # -----------------------------------------------

    if "Name / Description" not in df.columns:

        possible_description_columns = [
            "Description",
            "Name",
            "Transaction",
            "Merchant",
            "Details",
        ]

        found_description = None

        for column in possible_description_columns:

            if column in df.columns:
                found_description = column
                break

        if found_description is not None:

            df["Name / Description"] = (
                df[found_description].astype(str)
            )

        else:

            df["Name / Description"] = "Transaction"

    # -----------------------------------------------
    # Date
    # -----------------------------------------------

    if "Date" not in df.columns:

        possible_date_columns = [
            "Transaction Date",
            "transaction_date",
            "Timestamp",
        ]

        found_date = None

        for column in possible_date_columns:

            if column in df.columns:
                found_date = column
                break

        if found_date is not None:
            df["Date"] = df[found_date]

        else:
            raise ValueError(
                "Could not find a Date column in the CSV."
            )

    # -----------------------------------------------
    # Expense / Income
    # -----------------------------------------------

    if "Expense/Income" not in df.columns:

        possible_type_columns = [
            "Type",
            "Transaction Type",
            "transaction_type",
        ]

        found_type = None

        for column in possible_type_columns:

            if column in df.columns:
                found_type = column
                break

        if found_type is not None:

            df["Expense/Income"] = (
                df[found_type].astype(str)
            )

        else:

            # If there is no type column, infer it
            # from positive/negative amounts.

            df["Expense/Income"] = df["Amount (EUR)"].apply(
                lambda x: "Income" if x < 0 else "Expense"
            )

    # Normalize transaction type
    df["Expense/Income"] = (
        df["Expense/Income"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    # If CSV uses Credit/Debit
    df["Expense/Income"] = df["Expense/Income"].replace({
        "Debit": "Expense",
        "Credit": "Income",
        "Income": "Income",
        "Expense": "Expense",
    })

    # -----------------------------------------------
    # Date conversion
    # -----------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Date"]
    )

    return df


# ====================================================
# SIDEBAR
# ====================================================

st.sidebar.title("🚀 FinPilot AI")

user = st.session_state.user

st.sidebar.write(
    f"Logged in as: {user.email}"
)

if st.sidebar.button("Logout"):

    supabase = get_supabase()

    supabase.auth.sign_out()

    st.session_state.user = None

    st.rerun()


# ====================================================
# DISPLAY CURRENCY
# ====================================================

selected_currency = st.sidebar.selectbox(
    "Currency",
    ["EUR", "INR", "USD", "GBP"],
    index=0,
    key="display_currency"
)

currency_symbol = get_currency_symbol(
    selected_currency
)


# ====================================================
# NAVIGATION
# ====================================================

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📋 Transactions",
        "🤖 AI Insights",
        "💰 Savings Goal",
        "🎯 Budget Planner",
        "📄 Financial Report",
        "📈 Expense Forecast",
        "🔎 Spending Anomalies",
        "AI Finance Assistant",
    ]
)


# ====================================================
# TITLE
# ====================================================

st.title("💰 FinPilot AI")
st.subheader(
    "AI-Powered Personal Finance Dashboard"
)


# ====================================================
# SUPABASE
# ====================================================

supabase = get_supabase()

user = st.session_state.user


# ====================================================
# USER TRANSACTION DATA
# ====================================================

uploaded_file = st.file_uploader(
    "📂 Upload your bank statement (CSV)",
    type=["csv"]
)


# ====================================================
# UPLOADED CSV
# ====================================================

if uploaded_file is not None:

    try:

        original_df = pd.read_csv(
            uploaded_file
        )

        # -------------------------------------------
        # Detect currency automatically
        # -------------------------------------------

        detected_currency = detect_currency(
            original_df
        )

        if detected_currency is None:

            st.warning(
                "⚠️ We could not automatically detect "
                "the CSV currency."
            )

            detected_currency = st.selectbox(
                "Please select the CSV currency",
                ["INR", "EUR", "USD", "GBP"],
                key="csv_currency_fallback"
            )

        else:

            st.success(
                f"Detected CSV currency: "
                f"**{detected_currency}**"
            )

        # -------------------------------------------
        # Normalize CSV
        # -------------------------------------------

        prepared_df = prepare_dataframe(
            original_df
        )

        st.info(
            "Your uploaded transactions will be saved "
            "securely to your account."
        )

        save_mode = st.radio(
            "What should we do with this CSV?",
            [
                "Replace existing transactions",
                "Add to existing transactions"
            ],
            key="save_mode"
        )

        if st.button(
            "Save Transactions to My Account",
            type="primary"
        ):

            try:

                transactions = []

                for _, row in prepared_df.iterrows():

                    transaction = {
                        "user_id": str(user.id),

                        "transaction_date": (
                            row["Date"]
                            .date()
                            .isoformat()
                        ),

                        "description": str(
                            row["Name / Description"]
                        ),

                        "transaction_type": str(
                            row["Expense/Income"]
                        ),

                        "amount": float(
                            row["Amount (EUR)"]
                        ),

                        "category": str(
                            assign_category(
                                row["Name / Description"]
                            )
                        ),

                        "currency": detected_currency,
                    }

                    transactions.append(transaction)

                if save_mode == "Replace existing transactions":

                    supabase.table(
                        "transactions"
                    ).delete().eq(
                        "user_id",
                        str(user.id)
                    ).execute()

                    supabase.table(
                        "transactions"
                    ).insert(
                        transactions
                    ).execute()

                    st.success(
                        f"Replaced your previous data with "
                        f"{len(transactions)} transactions!"
                    )

                else:

                    existing_response = (
                        supabase
                        .table("transactions")
                        .select(
                            "transaction_date,description,"
                            "transaction_type,amount"
                        )
                        .eq(
                            "user_id",
                            str(user.id)
                        )
                        .execute()
                    )

                    existing_data = existing_response.data or []

                    existing_keys = set()

                    for existing in existing_data:

                        key = (
                            str(existing.get("transaction_date")),
                            str(
                                existing.get(
                                    "description",
                                    ""
                                )
                            ).strip().lower(),
                            str(
                                existing.get(
                                    "transaction_type",
                                    ""
                                )
                            ).strip().lower(),
                            round(
                                float(
                                    existing.get(
                                        "amount",
                                        0
                                    )
                                ),
                                2
                            )
                        )

                        existing_keys.add(key)

                    new_transactions = []
                    skipped_duplicates = 0

                    for transaction in transactions:

                        key = (
                            str(
                                transaction[
                                    "transaction_date"
                                ]
                            ),
                            str(
                                transaction[
                                    "description"
                                ]
                            ).strip().lower(),
                            str(
                                transaction[
                                    "transaction_type"
                                ]
                            ).strip().lower(),
                            round(
                                float(
                                    transaction[
                                        "amount"
                                    ]
                                ),
                                2
                            )
                        )

                        if key in existing_keys:

                            skipped_duplicates += 1

                        else:

                            new_transactions.append(
                                transaction
                            )

                            existing_keys.add(key)

                    if new_transactions:

                        supabase.table(
                            "transactions"
                        ).insert(
                            new_transactions
                        ).execute()

                    st.success(
                        f"Added {len(new_transactions)} "
                        f"new transactions!"
                    )

                    if skipped_duplicates > 0:

                        st.info(
                            f"Skipped {skipped_duplicates} "
                            f"duplicate transactions."
                        )

            except Exception as error:

                st.error(
                    "Could not save transactions."
                )

                st.code(
                    str(error)
                )

        # Use uploaded data for current session
        df = prepared_df.copy()

        # Store detected currency for conversion
        original_currency = detected_currency

        # Use uploaded data for current session
        df = prepared_df.copy()

        # Store detected currency for conversion
        original_currency = detected_currency

    except Exception as error:

        st.error(
            "Could not process this CSV file."
        )

        st.code(
            str(error)
        )

        st.stop()


# ====================================================
# LOAD SAVED DATA
# ====================================================

else:

    try:

        response = (
            supabase
            .table("transactions")
            .select("*")
            .eq(
                "user_id",
                str(user.id)
            )
            .execute()
        )

        saved_data = response.data

        if saved_data:

            df = pd.DataFrame(
                saved_data
            )

            # ---------------------------------------
            # Get original currency from database
            # ---------------------------------------

            currencies = (
                df["currency"]
                .dropna()
                .astype(str)
                .str.upper()
                .unique()
                .tolist()
            )

            if len(currencies) > 0:

                original_currency = currencies[0]

            else:

                original_currency = "EUR"

            # ---------------------------------------
            # Rename database columns
            # ---------------------------------------

            df = df.rename(
                columns={
                    "transaction_date": "Date",
                    "description": "Name / Description",
                    "transaction_type": "Expense/Income",
                    "amount": "Amount (EUR)",
                }
            )

            # Convert date
            df["Date"] = pd.to_datetime(
                df["Date"],
                errors="coerce"
            )

        else:

            # ---------------------------------------
            # New user
            # ---------------------------------------

            st.info(
                "👋 Welcome to FinPilot AI! "
                "Upload your bank statement to get started."
            )

            # Empty dataframe with expected columns
            df = pd.DataFrame(
                columns=[
                    "Date",
                    "Name / Description",
                    "Expense/Income",
                    "Amount (EUR)",
                ]
            )

            original_currency = "EUR"

    except Exception as error:

        st.error(
            "Could not load your financial data."
        )

        st.code(
            str(error)
        )

        st.stop()


# ====================================================
# HANDLE EMPTY DATA
# ====================================================

if df.empty:

    st.info(
        "📂 Upload a CSV bank statement above "
        "to start analyzing your finances."
    )

    st.stop()


# ====================================================
# CURRENCY CONVERSION
# ====================================================

try:

    df = convert_dataframe(
        df,
        original_currency,
        selected_currency
    )

except Exception as error:

    st.warning(
        "Currency conversion failed. "
        "Showing original values."
    )

    st.code(
        str(error)
    )


# ====================================================
# CATEGORIZE TRANSACTIONS
# ====================================================

df["Category"] = (
    df["Name / Description"]
    .apply(assign_category)
)


# ====================================================
# DATE
# ====================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

df = df.dropna(
    subset=["Date"]
)


# ====================================================
# CATEGORY FILTER
# ====================================================

categories = [
    "All"
] + sorted(
    df["Category"]
    .dropna()
    .unique()
    .tolist()
)

selected_category = st.sidebar.selectbox(
    "Category",
    categories,
    key="category_filter"
)


filtered_df = df.copy()

if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["Category"]
        == selected_category
    ]


# ====================================================
# DATE FILTER
# ====================================================

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="date_range"
)

if isinstance(
    start_date,
    tuple
):

    start_date, end_date = start_date


filtered_df = filtered_df[
    (filtered_df["Date"].dt.date >= start_date)
    &
    (filtered_df["Date"].dt.date <= end_date)
]


# ====================================================
# CALCULATE SUMMARY
# ====================================================

income, expense, savings = calculate_summary(
    filtered_df
)


# ====================================================
# FINANCIAL HEALTH
# ====================================================

health_score = financial_health_score(
    income,
    expense,
    savings
)


# ====================================================
# CATEGORY SPENDING
# ====================================================

category_spending = (
    filtered_df[
        filtered_df["Expense/Income"]
        == "Expense"
    ]
    .groupby("Category")["Amount (EUR)"]
    .sum()
    .reset_index()
)


# ====================================================
# DASHBOARD PAGE
# ====================================================

if page == "📊 Dashboard":

    st.header(
        "📊 Dashboard Overview"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Income",
        f"{currency_symbol}{income:.2f}"
    )

    col2.metric(
        "Expense",
        f"{currency_symbol}{expense:.2f}"
    )

    col3.metric(
        "Savings",
        f"{currency_symbol}{savings:.2f}"
    )

    st.subheader(
        "📊 Expense Distribution"
    )

    if not category_spending.empty:

        fig = px.pie(
            category_spending,
            names="Category",
            values="Amount (EUR)",
            hole=0.4,
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No expense data available."
        )

    st.subheader(
        "📈 Monthly Expense Trend"
    )

    expense_df = filtered_df[
        filtered_df["Expense/Income"]
        == "Expense"
    ].copy()

    if not expense_df.empty:

        monthly = (
            expense_df
            .groupby(
                expense_df["Date"]
                .dt.to_period("M")
            )["Amount (EUR)"]
            .sum()
            .reset_index()
        )

        monthly["Date"] = (
            monthly["Date"]
            .astype(str)
        )

        line_fig = px.line(
            monthly,
            x="Date",
            y="Amount (EUR)",
            markers=True,
            title="Monthly Expenses",
        )

        st.plotly_chart(
            line_fig,
            use_container_width=True
        )

    else:

        st.info(
            "No expense data available."
        )


# ====================================================
# TRANSACTIONS PAGE
# ====================================================

elif page == "📋 Transactions":

    st.header(
        "📋 Transactions"
    )

    search = st.text_input(
        "🔍 Search transaction"
    )

    transaction_df = filtered_df.copy()

    if search:

        transaction_df = transaction_df[
            transaction_df[
                "Name / Description"
            ]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    st.dataframe(
        transaction_df,
        use_container_width=True
    )


# ====================================================
# AI INSIGHTS PAGE
# ====================================================

elif page == "🤖 AI Insights":

    st.header(
        "🤖 AI Financial Insights"
    )

    st.metric(
        "⭐ Financial Health Score",
        f"{health_score}/100"
    )

    if health_score >= 85:

        st.success(
            "🟢 Excellent Financial Health"
        )

    elif health_score >= 65:

        st.info(
            "🟡 Good Financial Health"
        )

    elif health_score >= 45:

        st.warning(
            "🟠 Average Financial Health"
        )

    else:

        st.error(
            "🔴 Financial Health Needs Improvement"
        )

    st.success(
        f"Total Savings: "
        f"{currency_symbol}{savings:.2f}"
    )

    if not category_spending.empty:

        top_category = (
            category_spending
            .sort_values(
                "Amount (EUR)",
                ascending=False
            )
            .iloc[0]
        )

        st.warning(
            f"Highest spending category: "
            f"{top_category['Category']} "
            f"({currency_symbol}"
            f"{top_category['Amount (EUR)']:.2f})"
        )

    savings_rate = (
        (savings / income) * 100
        if income > 0
        else 0
    )

    st.metric(
        "📈 Savings Rate",
        f"{savings_rate:.1f}%"
    )

    if savings > expense:

        st.info(
            "✅ Excellent! Your savings exceed "
            "your expenses."
        )

    else:

        st.error(
            "⚠️ Try reducing your monthly expenses."
        )


# ====================================================
# SAVINGS GOAL
# ====================================================

elif page == "💰 Savings Goal":

    show_savings_goal(
        savings,
        currency_symbol
    )


# ====================================================
# BUDGET PLANNER
# ====================================================

elif page == "🎯 Budget Planner":

    show_budget_planner(
        filtered_df,
        currency_symbol
    )


# ====================================================
# FINANCIAL REPORT
# ====================================================

elif page == "📄 Financial Report":

    st.header(
        "Financial Report"
    )

    report = generate_financial_report(
        filtered_df,
        income,
        expense,
        savings,
        currency_symbol
    )

    st.text_area(
        "Report Preview",
        report,
        height=400
    )

    st.download_button(
        label="Download Financial Report",
        data=report,
        file_name="finpilot_financial_report.txt",
        mime="text/plain"
    )


# ====================================================
# EXPENSE FORECAST
# ====================================================

elif page == "📈 Expense Forecast":

    show_expense_forecast(
        filtered_df,
        currency_symbol
    )


# ====================================================
# SPENDING ANOMALIES
# ====================================================

elif page == "🔎 Spending Anomalies":

    show_anomaly_detection(
        filtered_df,
        currency_symbol
    )


# ====================================================
# AI FINANCE ASSISTANT
# ====================================================

elif page == "AI Finance Assistant":

    show_ai_chat(
        income,
        expense,
        savings,
        category_spending,
        currency_symbol
    )
