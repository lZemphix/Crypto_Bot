from logging import getLogger
from scripts.bot import Bot
from config.logger_config import load_logger_config
from src.consts import *

import random

from utils.telenotify import TeleNotify

logger = getLogger(__name__)

def main():
    
    load_logger_config(20)
    logger.info('bot was activated. Press "ctrl + c" for stop')
    
    # try:
    Bot().activate()
    # except Exception as e:
    #     err_id = random.randint(1_000_000,9_999_999)
    #     logger.error(f'Error id: {err_id}. Message:{e}')
    #     TeleNotify().error(CRUSH_MESSAGE.format(error_id=err_id))

if __name__ == '__main__':
    main()
    

