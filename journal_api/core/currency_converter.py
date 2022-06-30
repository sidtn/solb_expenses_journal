import datetime
from decimal import Decimal

import requests


class BadResponseFromCurrencyAPI(Exception):
    pass


class CurrencyRatesCache:

    """
    Takes named arguments in timedelta format.
    example: minutes=1, seconds=10
    """

    def __init__(self, **kwargs):
        self.cache = {}
        self.storage_time = kwargs

    def __call__(self, get_currency_rate_function):
        def get_rates(from_currency, to_currency):
            cached_rate = self.cache.get(f"{from_currency} - {to_currency}")
            if cached_rate and datetime.datetime.now() - cached_rate.get("created") < datetime.timedelta(**self.storage_time):
                rate = cached_rate.get("rate")
                return rate
            else:
                rate = get_currency_rate_function(from_currency, to_currency)
                self.cache[f"{from_currency} - {to_currency}"] = {"rate": rate, "created": datetime.datetime.now()}
                return rate
        return get_rates


@CurrencyRatesCache(seconds=10)
def currency_converter(from_currency, to_currency):
    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}"
    response = requests.get(url)
    result = response
    try:
        rate = result.json()["result"]
        return Decimal(rate)
    except KeyError:
        print(result.json())
        raise BadResponseFromCurrencyAPI(
            "no correct response from currency api"
        )
