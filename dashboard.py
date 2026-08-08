import streamlit as st
import pandas as pd
import plotly.express as px

from src.categorizer import assign_category
from src.analyzer import (
    calculate_summary,
    financial_health_score,
)
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
# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(page_title="FinPilot AI", layout="wide")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🚀 FinPilot AI")
selected_currency = st.sidebar.selectbox(
    "Currency",
    ["EUR", "INR", "USD", "GBP"],
    index=0
)

currency_symbol = get_currency_symbol(selected_currency)

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

# -----------------------------
# Title
# -----------------------------
st.title("💰 FinPilot AI")
st.subheader("AI-Powered Personal Finance Dashboard")

# -----------------------------
# Upload CSV
# -----------------------------
uploaded_file = st.file_uploader(
    "📂 Upload your bank statement (CSV)",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("data/transactions_2022_2023.csv")
original_currency = "EUR"

df = convert_dataframe(
    df,
    original_currency,
    selected_currency
)
# -----------------------------
# Categorize Transactions
# -----------------------------
df["Category"] = df["Name / Description"].apply(assign_category)
# Convert Date column
df["Date"] = pd.to_datetime(df["Date"])
# -----------------------------
# Category Filter
# -----------------------------
categories = ["All"] + sorted(df["Category"].unique().tolist())

selected_category = st.sidebar.selectbox(
    "Category",
    categories
)

filtered_df = df.copy()

if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["Category"] == selected_category
    ]
# -----------------------------
# Date Filter
# -----------------------------
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(start_date, tuple):
    start_date, end_date = start_date

filtered_df = filtered_df[
    (filtered_df["Date"].dt.date >= start_date) &
    (filtered_df["Date"].dt.date <= end_date)
]
# -----------------------------
# Calculate Summary
# -----------------------------
income, expense, savings = calculate_summary(filtered_df)
health_score = financial_health_score(
    income,
    expense,
    savings
)

category_spending = (
    filtered_df[filtered_df["Expense/Income"] == "Expense"]
    .groupby("Category")["Amount (EUR)"]
    .sum()
    .reset_index()
)

# ====================================================
# DASHBOARD PAGE
# ====================================================
if page == "📊 Dashboard":

    st.header("📊 Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Income", f"{currency_symbol}{income:.2f}")
    col2.metric("Expense", f"{currency_symbol}{expense:.2f}")
    col3.metric("Savings", f"{currency_symbol}{savings:.2f}")

    st.subheader("📊 Expense Distribution")

    fig = px.pie(
        category_spending,
        names="Category",
        values="Amount (EUR)",
        hole=0.4,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Monthly Expense Trend")

    expense_df = filtered_df[
    filtered_df["Expense/Income"] == "Expense"
].copy()
    expense_df["Date"] = pd.to_datetime(expense_df["Date"])

    monthly = (
        expense_df.groupby(
            expense_df["Date"].dt.to_period("M")
        )["Amount (EUR)"]
        .sum()
        .reset_index()
    )

    monthly["Date"] = monthly["Date"].astype(str)

    line_fig = px.line(
        monthly,
        x="Date",
        y="Amount (EUR)",
        markers=True,
        title="Monthly Expenses",
    )

    st.plotly_chart(line_fig, use_container_width=True)

# ====================================================
# TRANSACTIONS PAGE
# ====================================================
elif page == "📋 Transactions":

    st.header("📋 Transactions")

    search = st.text_input("🔍 Search transaction")

    transaction_df = filtered_df.copy()

    if search:
        transaction_df = transaction_df[
          transaction_df["Name / Description"].str.contains(
            search,
            case=False,
            na=False
   )  
]

    st.dataframe(transaction_df, use_container_width=True)

# ====================================================
# AI INSIGHTS PAGE
# ====================================================
elif page == "🤖 AI Insights":

    st.header("🤖 AI Financial Insights")
    st.metric(
    "⭐ Financial Health Score",
    f"{health_score}/100"
)
if health_score >= 85:
     st.success("🟢 Excellent Financial Health")
elif health_score >= 65:
    st.info("🟡 Good Financial Health")
elif health_score >= 45:
    st.warning("🟠 Average Financial Health")
else:
    st.error("🔴 Financial Health Needs Improvement")


    st.success(
    f"Total Savings: {currency_symbol}{savings:.2f}"
)

    top_category = category_spending.sort_values(
        "Amount (EUR)",
        ascending=False
    ).iloc[0]

    st.warning(
        f"Highest spending category: "
        f"{top_category['Category']} "
        f"({currency_symbol}{top_category['Amount (EUR)']:.2f})")

    savings_rate = (savings / income) * 100 if income > 0 else 0

    st.metric("📈 Savings Rate", f"{savings_rate:.1f}%")

    if savings > expense:
        st.info("✅ Excellent! Your savings exceed your expenses.")
    else:
        st.error("⚠️ Try reducing your monthly expenses.")

if page == "💰 Savings Goal":

    show_savings_goal(
        savings,
        currency_symbol
    )
if page == "🎯 Budget Planner":

    show_budget_planner(
        filtered_df,
        currency_symbol
    ) 
if page == "📄 Financial Report":

    st.header("Financial Report")

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
if page == "📈 Expense Forecast":

    show_expense_forecast(
        filtered_df,
        currency_symbol
    )  
if page == "🔎 Spending Anomalies":

    show_anomaly_detection(
        filtered_df,
        currency_symbol
    )  
if page == "AI Finance Assistant":

    show_ai_chat(
        income,
        expense,
        savings,
        category_spending,
        currency_symbol
    )        