import json

def get_config():
    with open('bot_config.json') as f:
        context = json.load(f)
    return context