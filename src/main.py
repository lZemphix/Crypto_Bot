from logging import getLogger
import sys
from scripts.bot import Bot
from config.logger_config import load_logger_config
from data.consts import *
import traceback

import random
from utils.telenotify import Telenotify

logger = getLogger(__name__)


def main():

    load_logger_config(20)
    logger.info('bot was activated. Press "ctrl + c" for stop')

    try:
        Bot().activate()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        err_id = random.randint(1_000_000, 9_999_999)
        traceback.print_exception(type(e), e, e.__traceback__)
        logger.error(f"Error id: {err_id}. Message:{e}")
        Telenotify().error(CRUSH_MESSAGE.format(error_id=err_id))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bot was stoped")
        sys.exit(0)
