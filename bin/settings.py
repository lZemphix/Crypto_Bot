import json

from data.consts import SETTINGS_MENU


def change_config(param: str, new_value: str | int | bool):
    with open("bot_config.json", "r") as f:
        c = json.load(f)
        c[param] = new_value

    with open("bot_config.json", "w") as f:
        json.dump(c, f, indent=4)


def settings():
    with open("bot_config.json", "r") as f:
        config = json.load(f)

    choice = int(
        input(
            SETTINGS_MENU.format(
                sybmol=config["symbol"],
                interval=config["interval"],
                amount=config["amountBuy"],
                rsi=config["RSI"],
                buy=config["stepBuy"],
                sell=config["stepSell"],
                notifies=config["send_notify"],
            )
        )
    )

    match choice:
        case 1:
            new_value = input(
                "Send new pair name (BTCUSD, SOLUSDT, ETHUSDT and etc.) [BTCUSDT]\n>>> "
            )
            change_config("symbol", new_value if new_value != "" else "BTCUSDT")
            print("Changes saved!")
            settings()
        case 2:
            new_value = input(
                "Send new graph interval (1,5,10,15,30,60,120,240,360,720) [5]\n>>> "
            )
            if new_value == "":
                change_config("interval", 5)
            else:
                change_config("interval", int(new_value))
            print("Changes saved!")
            settings()
        case 3:
            new_value = input(
                "Send new order price (min. 5. Recommended 10-15% of your balance) [5]\n>>> "
            )
            if new_value == "":
                change_config("amountBuy", 5)
            elif int(new_value) < 5:
                print("Aborting. Min. order price = 5.5!")
                settings()
            else:
                change_config("amountBuy", int(new_value))
            print("Changes saved!")
            settings()
        case 4:
            new_value = input("Send new RSI value (Recommended 39-42) [41]\n>>> ")
            if new_value == "":
                change_config("RSI", 5)
            else:
                change_config("RSI", int(new_value))
            print("Changes saved!")
            settings()
        case 5:
            new_value = input(
                "Send new value for buy step (Recommended 0.3-1% of pair price) [750]\n>>> "
            )
            if new_value == "":
                change_config("stepBuy", 750)
            else:
                change_config("stepBuy", int(new_value))
            new_value = input(
                "Send new value for sell step (Recommended 0.3-1% of pair price) [650]\n>>> "
            )
            if new_value == "":
                change_config("stepSell", 650)
            else:
                change_config("stepSell", int(new_value))
            print("Changes saved!")
            settings()
        case 6:
            new_value = input(
                "Turn on sending notifies to telegram [y/n](Recommended turn on!) [y]\n>>> "
            )
            if new_value == "y":
                new_value = True
            elif new_value == "n":
                new_value = False
            change_config("send_notify", new_value if new_value != "" else False)
            print("Changes saved!")
            settings()
        case 7:
            change_config("symbol", "BTCUSDT")
            change_config("interval", 5)
            change_config("amountBuy", 5.5)
            change_config("RSI", 41)
            change_config("stepBuy", 750)
            change_config("symbol", 650)
            change_config("send_notify", False)

            print("Config was reset!")
            settings()
