import pandas as pd

CURRENCY_RATES = {
    "EUR": 1.0,
    "INR": 90.0,
    "USD": 1.17,
    "GBP": 0.86,
}

CURRENCY_SYMBOLS = {
    "EUR": "€",
    "INR": "₹",
    "USD": "$",
    "GBP": "£",
}


def convert_amount(amount, from_currency, to_currency):
    """
    Convert an amount from the source currency to the selected currency.
    """

    if from_currency == to_currency:
        return amount

    amount_in_eur = amount / CURRENCY_RATES[from_currency]

    return amount_in_eur * CURRENCY_RATES[to_currency]


def convert_dataframe(df, from_currency, to_currency):
    """
    Convert transaction amounts to the selected currency.
    """

    df = df.copy()

    df["Amount (EUR)"] = df["Amount (EUR)"].apply(
        lambda amount: convert_amount(
            amount,
            from_currency,
            to_currency
        )
    )

    return df


def get_currency_symbol(currency):
    return CURRENCY_SYMBOLS.get(currency, currency)