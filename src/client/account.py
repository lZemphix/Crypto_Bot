import json
from utils.exceptions import NoCryptoCurrencyException


class Account:

    def __init__(self) -> None:
        super().__init__()

    def get_balance(self) -> dict:

        try:
            coin_values = {}
            with open("src/data/gatekeeper_journal.json") as f:
                journal = json.load(f)
            balance = journal["balance"]["data"]["coin"]
            for n in range(len(balance)):
                coin_values[balance[n].get("coin")] = float(
                    balance[n].get("walletBalance")
                )
            return coin_values
        except Exception:
            raise NoCryptoCurrencyException("No cryptocurrencies found!")


account = Account()
