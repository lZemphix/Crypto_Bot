import json
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from utils.balance import get_balance

from utils.auth import verify

templates = Jinja2Templates(directory="web/templates")
router = APIRouter()


@router.get("/", dependencies=[Depends(verify)])
async def index(request: Request):
    with open("bot_config.json") as f:
        conf = json.load(f)
    with open('metadata.json') as f:
        metadata = json.load(f)
    coin_name = conf["symbol"].replace("USDT", "")
    balance = get_balance()
    context = {
        "status": "on",
        "pair": conf["symbol"],
        "balanceq": balance["USDT"],
        "balanceb": balance[coin_name],
        "interval": conf["interval"],
    } | metadata
    return templates.TemplateResponse(
        request=request, name="index.html", context=context
    )
