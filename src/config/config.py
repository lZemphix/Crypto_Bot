import json
import os
from logging import getLogger

logger = getLogger(__name__)


def get_bot_config(param: str = None):
    try:
        with open("src/config/bot_config.json", "r") as f:
            config: dict = json.load(f)
            if param == None:
                return config
            return config.get(param)
    except Exception as e:
        logger.error(e)


def get_env_config(param: str = None) -> dict:
    try:
        keys = "API_KEY API_KEY_SECRET ACCOUNT_TYPE BOT_TOKEN CHAT_ID".split()
        values = [os.getenv(key) for key in keys]
        config = {}
        for key, value in zip(keys, values):
            config[key] = value
        return config.get(param)
    except Exception as e:
        logger.error(e)
