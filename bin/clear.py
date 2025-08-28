import json


def clear():
    with open("src/data/trade_journal.json", "r") as f:
        j = json.load(f)

    default_trade_journal = {
        "laps": 0,
        "orders": [],
        "buy_lines": [],
        "sell_lines": [],
    }

    with open("src/data/trade_journal.json", "w") as f:
        json.dump(default_trade_journal, f, indent=4)
