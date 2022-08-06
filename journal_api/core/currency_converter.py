import datetime
from decimal import Decimal

import requests
from django.conf import settings


class BadResponseFromCurrencyAPI(Exception):
    pass


class CurrencyRatesCache:

    """
    Takes named argument storage_time in seconds.
    Default: 20 seconds
    """

    def __init__(self, func=None, storage_time=20):
        self.cache = {}
        self._storage_time = storage_time
        self._func = func

    def get_rates(self, from_currency, to_currency):
        cached_rate = self.cache.get(f"{from_currency} - {to_currency}")
        if cached_rate and datetime.datetime.now() - cached_rate.get(
            "created"
        ) < datetime.timedelta(seconds=self._storage_time):
            rate = cached_rate.get("rate")
            return rate
        else:
            rate = self._func(from_currency, to_currency)
            self.cache[f"{from_currency} - {to_currency}"] = {
                "rate": rate,
                "created": datetime.datetime.now(),
            }
            return rate

    def __call__(self, *args):
        if callable(args[0]):
            self._func = args[0]
            return self.get_rates
        return self.get_rates(*args)


@CurrencyRatesCache(storage_time=settings.CURRENCY_CACHE_LIFETIME)
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
