from client.base import Client
from utils.exceptions import NoCryptoCurrencyException


class Account(Client):

    def __init__(self) -> None:
        super().__init__()

    def get_balance(self) -> dict:
        try:
            coin_values = {}
            get_balance = self.client.get_wallet_balance(accountType=self.ACCOUNT_TYPE)[
                "result"
            ]["list"][0]["coin"]
            for n in range(len(get_balance)):
                coin_values[get_balance[n].get("coin")] = float(
                    get_balance[n].get("walletBalance")
                )
            return coin_values
        except Exception:
            raise NoCryptoCurrencyException("No cryptocurrencies found!")


account = Account()
