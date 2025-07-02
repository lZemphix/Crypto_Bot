BOT_STARTED_MESSAGE = """Bot was started!
```
Pair: {symbol}
Interval: {interval} min
Order price: {amount_buy} USDT
---Balance---
USDT: {usdt_balance}
{coin_name}: {coin_balance}```"""

CRUSH_MESSAGE = """Bot was stopped!
```
Error id: {error_id}
Message: send this error id to developer```"""

FIRST_BUY_MESSAGE = """```
Buy price: {buy_price}
Balance: {balance}
Sell line: {sell_line}
Average line: {buy_line}```"""

SETTINGS_MENU = """Bot Settings Menu

Select the necessary option:
    1. Change trade pair [{sybmol}]
    2. Change interval [{interval}]
    3. Change order price [{amount}]
    4. Change RSI [{rsi}]
    5. Change buy/sell step [{buy}/{sell}]
    6. Turn on/off telegram notifies [{notifies}]
    7. Reset settings
    
"ctrl + c" for cancel
>>> """

CMX_HELP = """args:
    clear               - clears buy history (useful if bot bought and you close the position manually)
    settings            - open bot settings
    start               - start the bot
    help [-h | --help]  - show this message
    """