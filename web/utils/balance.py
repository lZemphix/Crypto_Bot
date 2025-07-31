from pybit.unified_trading import HTTP
import os

account_type = os.getenv('ACCOUNT_TYPE')
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_KEY_SECRET')

print(account_type, api_key, api_secret)

client = HTTP(
            testnet=False,
            api_key=api_key,
            api_secret=api_secret,
        )

def get_balance():
    balance = client.get_wallet_balance(accountType=account_type)
    formated_balance = {}
    coins: dict = balance['result']['list'][0]['coin']
    for n in range(len(coins)):
            formated_balance[coins[n].get("coin")] = float(
                coins[n].get("walletBalance")
            )
    return formated_balance

    