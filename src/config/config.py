import json
import os

def get_bot_config(param: str = None):
    try:
        with open('src/config/bot_config.json', 'r') as f:
            config: dict = json.load(f)
            if param == None:
                return config
            return config.get(param)
    except Exception as e:
        print(e)

def get_env_config(param: str = None) -> dict:
    keys = "API_KEY API_KEY_SECRET ACCOUNT_TYPE BOT_TOKEN CHAT_ID".split()
    values = [os.getenv(key) for key in keys]
    config = {}
    for key, value in zip(keys, values):
        config[key] = value
    return config.get(param)
        
