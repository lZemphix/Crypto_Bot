import os
import time
import logging
from datetime import datetime, timezone

from pybit.unified_trading import HTTP

logger = logging.getLogger(__name__)


def get_historical_klines(start_time_ms: int, symbol: str, interval: str) -> list:
    """
    Fetches historical kline data from ByBit, handling pagination correctly by fetching
    data backwards in time from now until the specified start time.

    :param start_time_ms: The start time in milliseconds timestamp.
    :param symbol: The trading symbol (e.g., 'BTCUSDT').
    :param interval: The kline interval (e.g., '5', '60', '720').
    :return: A list of klines, sorted from oldest to newest.
    """
    session = HTTP(
        testnet=False,
        api_key=os.getenv("API_KEY"),
        api_secret=os.getenv("API_KEY_SECRET"),
    )

    all_klines = []
    end_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    while True:
        response = session.get_kline(
            category="spot",
            symbol=symbol,
            interval=interval,
            end=end_time_ms,
            limit=1000,
        )

        if response.get("retCode") == 0 and response.get("result", {}).get("list"):
            klines = response["result"]["list"]
            oldest_kline_time = int(klines[-1][0])

            klines_in_range = [k for k in klines if int(k[0]) >= start_time_ms]
            all_klines.extend(klines_in_range)

            if oldest_kline_time < start_time_ms or len(klines) < 1000:
                break

            end_time_ms = oldest_kline_time
        else:
            print(f"ByBit API returned an error or no data. Response: {response}")
            break

        time.sleep(0.2)

    return sorted(all_klines, key=lambda k: int(k[0]))
