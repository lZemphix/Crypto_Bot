import json
import os
from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv, set_key
from utils.auth import verify

load_dotenv()

templates = Jinja2Templates(directory="web/templates")

router = APIRouter(prefix="/settings")


@router.get("/", dependencies=[Depends(verify)])
async def settings(request: Request):
    with open("bot_config.json") as f:
        context = json.load(f)
    keys = "ACCOUNT_TYPE API_KEY_SECRET API_KEY BOT_TOKEN CHAT_ID".split()
    for key in keys:
        context[key] = os.getenv(key)
    return templates.TemplateResponse(
        request=request, name="settings.html", context=context
    )


@router.post("/")
async def handle_form(
    request: Request,
    symbol: str = Form(...),
    interval: int = Form(...),
    amountBuy: float = Form(...),
    RSI: int = Form(...),
    stepBuy: float = Form(...),
    stepSell: float = Form(...),
    send_notify: bool = Form(default=False),
    ACCOUNT_TYPE: str = Form(...),
    API_KEY_SECRET: str = Form(...),
    API_KEY: str = Form(...),
    BOT_TOKEN: str = Form(...),
    CHAT_ID: str = Form(...),
):
    keys = "ACCOUNT_TYPE API_KEY_SECRET API_KEY BOT_TOKEN CHAT_ID".split()
    settings_form = {
        "symbol": symbol,
        "interval": interval,
        "amountBuy": amountBuy,
        "RSI": RSI,
        "stepBuy": stepBuy,
        "stepSell": stepSell,
        "send_notify": send_notify,
    }
    set_key(".env", "ACCOUNT_TYPE", ACCOUNT_TYPE)
    set_key(".env", "API_KEY_SECRET", API_KEY_SECRET)
    set_key(".env", "API_KEY", API_KEY)
    set_key(".env", "BOT_TOKEN", BOT_TOKEN)
    set_key(".env", "CHAT_ID", CHAT_ID)
    with open("bot_config.json", "w") as f:
        json.dump(settings_form, f, indent=4)
    with open("bot_config.json") as f:
        context = json.load(f)
    for key in keys:
        context[key] = os.getenv(key)
    return templates.TemplateResponse(
        request=request, name="settings.html", context=context
    )
