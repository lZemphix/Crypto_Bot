import json
from datetime import datetime
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from .chart_generator import generate_trade_chart
from utils.bybit_client import get_historical_klines
from utils.telegram_sender import send_chart_to_telegram


templates = Jinja2Templates(directory="web/templates")

router = APIRouter(prefix="/statistic")


@router.get("/")
async def settings(request: Request):
    return templates.TemplateResponse(request=request, name="statistic.html")


@router.get("/send-chart")
async def send_chart():
    with open("metadata.json") as f:
        trade_history = json.load(f).get("previous_actions", {})
    with open("bot_config.json") as f:
        bot_config = json.load(f)

    all_actions = trade_history.get("buy_actions", []) + trade_history.get(
        "sell_actions", []
    )
    if not all_actions:
        return JSONResponse(
            content={
                "ok": False,
                "error": "No trade actions found to generate a chart.",
            },
            status_code=404,
        )

    valid_actions = [t for t in all_actions if isinstance(t, dict) and "datetime" in t]
    if not valid_actions:
        return JSONResponse(
            content={
                "ok": False,
                "error": "No valid trade actions with datetime found.",
            },
            status_code=404,
        )

    start_datetime_str = min(t["datetime"] for t in valid_actions)
    start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
    start_timestamp_ms = int(start_datetime.timestamp() * 1000)

    klines = get_historical_klines(
        start_time_ms=start_timestamp_ms,
        symbol=bot_config["symbol"],
        interval=str(bot_config["interval"]),
    )

    if not klines:
        return JSONResponse(
            content={"ok": False, "error": "Could not fetch kline data."},
            status_code=404,
        )

    chart_buffer = await generate_trade_chart(klines, trade_history)

    tg_response = send_chart_to_telegram(chart_buffer)

    if tg_response.get("ok"):
        return JSONResponse(
            content={"ok": True, "message": "Chart sent to Telegram successfully!"}
        )
    else:
        return JSONResponse(
            content={
                "ok": False,
                "error": tg_response.get("error", "Unknown error sending to Telegram"),
            },
            status_code=500,
        )
