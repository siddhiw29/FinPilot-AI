import streamlit as st
import pandas as pd
import plotly.express as px

from src.categorizer import assign_category
from src.analyzer import calculate_summary

st.set_page_config(page_title="FinPilot AI", layout="wide")

st.title(" FinPilot AI")
st.subheader("AI-Powered Personal Finance Dashboard")

# Load data
df = pd.read_csv("data/transactions_2022_2023.csv")

# Categorize transactions
df["Category"] = df["Name / Description"].apply(assign_category)

# Calculate summary
income, expense, savings = calculate_summary(df)
category_spending = (
    df[df["Expense/Income"] == "Expense"]
    .groupby("Category")["Amount (EUR)"]
    .sum()
    .reset_index()
)

# Dashboard cards
col1, col2, col3 = st.columns(3)

col1.metric(" Income", f"€{income:.2f}")
col2.metric(" Expense", f"€{expense:.2f}")
col3.metric(" Savings", f"€{savings:.2f}")
st.subheader("📊 Expense Distribution")

fig = px.pie(
    category_spending,
    names="Category",
    values="Amount (EUR)",
    hole=0.4,
)

st.plotly_chart(fig, use_container_width=True)
st.subheader(" Monthly Expense Trend")

expense_df = df[df["Expense/Income"] == "Expense"].copy()
expense_df["Date"] = pd.to_datetime(expense_df["Date"])

monthly = (
    expense_df
    .groupby(expense_df["Date"].dt.to_period("M"))["Amount (EUR)"]
    .sum()
    .reset_index()
)

monthly["Date"] = monthly["Date"].astype(str)

line_fig = px.line(
    monthly,
    x="Date",
    y="Amount (EUR)",
    markers=True,
    title="Monthly Expenses"
)

st.plotly_chart(line_fig, use_container_width=True)