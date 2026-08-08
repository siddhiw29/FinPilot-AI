# FinPilot AI

FinPilot AI is a Python-based personal finance analytics application that helps users analyze bank transactions, automatically categorize expenses, visualize spending patterns, and gain actionable financial insights through an interactive dashboard.

---

## Overview

Managing personal finances can be challenging when dealing with large volumes of bank transactions. FinPilot AI simplifies this process by automatically categorizing expenses, summarizing financial data, and presenting insights through interactive visualizations. Users can upload their own bank statements in CSV format to analyze their spending habits and monitor their financial health.

---

## Features

- Upload and analyze bank statements in CSV format
- Automatic expense categorization
- Interactive dashboard with financial summaries
- Income, Expense, and Savings overview
- Expense Distribution visualization
- Monthly Expense Trend analysis
- Financial Health Score
- Search and filter transactions
- AI-generated financial insights and recommendations

---

## Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### Data Processing
- Pandas
- NumPy

### Data Visualization
- Plotly

### AI
- Ollama
- Llama 2

---

## Project Structure

```text
FinPilot-AI/
│
├── app.py
├── dashboard.py
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── data/
│   ├── transactions_2022_2023.csv
│   └── categorized_transactions.csv
│
├── notebooks/
│   ├── categorize_expenses.ipynb
│   ├── categorize_expenses_with_validation.ipynb
│   ├── dashboard.ipynb
│   ├── expense_classifier.ipynb
│   ├── expense_validation.ipynb
│   ├── financial_insights.ipynb
│   └── finpilot_dashboard.ipynb
│
└── src/
    ├── analyzer.py
    ├── categorizer.py
    └── recommendations.py
```

---


## Application Modules

### Dashboard

Displays:

- Total Income
- Total Expense
- Total Savings
- Expense Distribution Chart
- Monthly Expense Trend

### Transactions

Allows users to:

- Search transactions
- View categorized transaction history
- Analyze uploaded bank statements

### AI Insights

Provides:

- Financial Health Score
- Savings Rate
- Highest Spending Category
- Personalized financial recommendations

---

## Future Enhancements

- Budget Planner
- Savings Goal Tracker
- Expense Forecasting
- PDF Report Generation
- AI Chat Assistant
- Spending Anomaly Detection
- Multi-user Authentication
- Cloud Deployment

---

## Author

**Siddhi Waje**

GitHub: https://github.com/siddhiw29
