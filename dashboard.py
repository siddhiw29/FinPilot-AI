import streamlit as st
import pandas as pd
import plotly.express as px

from src.categorizer import assign_category
from src.analyzer import (
    calculate_summary,
    financial_health_score,
)

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(page_title="FinPilot AI", layout="wide")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🚀 FinPilot AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📋 Transactions",
        "🤖 AI Insights"
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

# -----------------------------
# Categorize Transactions
# -----------------------------
df["Category"] = df["Name / Description"].apply(assign_category)

# -----------------------------
# Calculate Summary
# -----------------------------
income, expense, savings = calculate_summary(df)
health_score = financial_health_score(
    income,
    expense,
    savings
)

category_spending = (
    df[df["Expense/Income"] == "Expense"]
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

    col1.metric("💰 Income", f"€{income:.2f}")
    col2.metric("💸 Expense", f"€{expense:.2f}")
    col3.metric("💵 Savings", f"€{savings:.2f}")

    st.subheader("📊 Expense Distribution")

    fig = px.pie(
        category_spending,
        names="Category",
        values="Amount (EUR)",
        hole=0.4,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Monthly Expense Trend")

    expense_df = df[df["Expense/Income"] == "Expense"].copy()
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

    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df["Name / Description"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    st.dataframe(filtered_df, use_container_width=True)

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


    st.success(f"💰 Total Savings: €{savings:.2f}")

    top_category = category_spending.sort_values(
        "Amount (EUR)",
        ascending=False
    ).iloc[0]

    st.warning(
        f"Highest spending category: "
        f"{top_category['Category']} "
        f"(€{top_category['Amount (EUR)']:.2f})"
    )

    savings_rate = (savings / income) * 100 if income > 0 else 0

    st.metric("📈 Savings Rate", f"{savings_rate:.1f}%")

    if savings > expense:
        st.info("✅ Excellent! Your savings exceed your expenses.")
    else:
        st.error("⚠️ Try reducing your monthly expenses.")