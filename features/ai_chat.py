import streamlit as st
import ollama


def ask_local_ai(
    question,
    income,
    expense,
    savings,
    savings_rate,
    category_spending,
    currency_symbol
):

    if category_spending.empty:
        top_category = "No expense category available"
        top_amount = 0
    else:
        top = category_spending.iloc[0]
        top_category = top["Category"]
        top_amount = top["Amount (EUR)"]

    prompt = f"""
You are FinPilot AI, a personal finance assistant.

Answer the user's question using the financial information
provided below.

Financial information:

Income: {currency_symbol}{income:.2f}
Total Expenses: {currency_symbol}{expense:.2f}
Savings: {currency_symbol}{savings:.2f}
Savings Rate: {savings_rate:.1f}%

Highest Spending Category:
{top_category}

Amount spent in highest category:
{currency_symbol}{top_amount:.2f}

User Question:
{question}

Rules:
- Give a direct answer to the user's question.
- Use the financial data above.
- Do not invent transactions or numbers.
- Give practical suggestions when useful.
- Keep the answer concise and easy to understand.
- Do not provide professional investment, tax, or legal advice.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


def show_ai_chat(
    income,
    expense,
    savings,
    category_spending,
    currency_symbol
):

    st.header("AI Finance Assistant")

    st.write(
        "Ask questions about your financial data "
        "and receive personalized insights."
    )

    savings_rate = (
        (savings / income) * 100
        if income > 0
        else 0
    )

    question = st.text_input(
        "Ask FinPilot AI",
        placeholder="How can I reduce my expenses?"
    )

    if question:

        with st.spinner(
            "FinPilot AI is thinking..."
        ):

            try:

                response = ask_local_ai(
                    question,
                    income,
                    expense,
                    savings,
                    savings_rate,
                    category_spending,
                    currency_symbol
                )

                st.subheader("FinPilot AI")

                st.write(response)

            except Exception as error:

                st.error(
                    "Could not connect to Llama 3.2."
                )

                st.code(str(error))