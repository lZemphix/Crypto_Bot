#!/usr/bin/env python
import os
import sys
from src.data.consts import *
from src.utils.lines_manager import LinesManager
from src.utils.journal_manager import JournalManager

from clear import clear
from settings import settings


def help():
    print(CMX_HELP)


def buy(): 
    order_price = sys.argv[1]
    orders = data['orders']
    orders.append(order_price)
    LinesManager().write_lines(orders / len(orders))
    data = JournalManager().get()
    data['orders'] = orders
    JournalManager().update(data)
    print('Fake buy was added')

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        help()
        return

    match args[0]:
        case "help" | "-h" | "--help":
            help()

        case "clear":
            clear()
            print("Trade journal was returned to base state")

        case "start":
            os.system("python3 src/main.py")

        case "settings":
            try:
                settings()
            except KeyboardInterrupt:
                print("\nExit")

        case "buy":
            buy()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShut down")
