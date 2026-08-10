import requests
import streamlit as st


CURRENCY_SYMBOLS = {
    "EUR": "€",
    "INR": "₹",
    "USD": "$",
    "GBP": "£",
}


@st.cache_data(ttl=3600)
def get_exchange_rate(base_currency, target_currency):

    if base_currency == target_currency:
        return 1.0

    url = (
        f"https://api.frankfurter.app/latest"
        f"?from={base_currency}"
        f"&to={target_currency}"
    )

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return data["rates"][target_currency]


def get_currency_symbol(currency):

    return CURRENCY_SYMBOLS.get(
        currency,
        currency
    )


def convert_dataframe(
    df,
    base_currency,
    target_currency
):

    converted_df = df.copy()

    rate = get_exchange_rate(
        base_currency,
        target_currency
    )

    converted_df["Amount (EUR)"] = (
        converted_df["Amount (EUR)"] * rate
    )

    return converted_df