import json
from dotenv import load_dotenv
import requests
import os

load_dotenv()


def get_currencies():
    url = "https://api.apilayer.com/currency_data/list"
    headers = {"apikey": os.getenv("API_KEY_CURRENCY")}
    response = requests.request("GET", url, headers=headers)
    result = response.json()["currencies"]
    currencies_list = []
    for code, name in result.items():
        currencies_dict = {
            "fields": {"name": name},
            "model": "journal_api.currency",
            "pk": code,
        }
        currencies_list.append(currencies_dict)

    with open("../currencies.json", "w", encoding="utf8") as json_file:
        json_data = json.dumps(
            currencies_list, ensure_ascii=False, sort_keys=True, indent=4
        )
        json_file.write(json_data)


if __name__ == "__main__":
    get_currencies()
