import os
from decimal import Decimal

import requests
from dotenv import load_dotenv

load_dotenv()


class BadResponseFromCurrencyAPI(Exception):
    pass


def currency_converter(from_currency, to_currency, amount):
    # headers = {"apikey": os.getenv("API_KEY_CURRENCY")}
    # url = f"https://api.apilayer.com/currency_data/convert?to={to_currency}&from={from_currency}&amount={amount}"
    # response = requests.request("GET", url, headers=headers)
    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}"
    response = requests.get(url)
    result = response
    try:
        rate = result.json()["result"]
        return Decimal(rate) * amount
    except KeyError:
        print(result.json())
        raise BadResponseFromCurrencyAPI(
            "no correct response from currency api"
        )
