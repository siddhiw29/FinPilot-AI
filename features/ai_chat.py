import streamlit as st
from google import genai


def ask_cloud_ai(
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

Analyze the user's financial information and answer their question.

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

Instructions:
- Answer the user's actual question.
- Use the provided financial data.
- Do not invent transactions or numbers.
- Give practical suggestions when appropriate.
- Keep the answer concise and easy to understand.
- Do not provide professional investment, tax, or legal advice.
"""

    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


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
            "FinPilot AI is analyzing your finances..."
        ):

            try:

                response = ask_cloud_ai(
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
                    "Unable to connect to FinPilot AI."
                )

                st.code(str(error))