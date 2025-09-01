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
    :param interval: The kline interval (e.g., '5', '60', 'D').
    :return: A list of klines, sorted from oldest to newest.
    """
    session = HTTP(
        testnet=False,
        api_key=os.getenv("API_KEY"),
        api_secret=os.getenv("API_KEY_SECRET"),
    )

    all_klines = []
    # Start fetching from now backwards
    end_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    while True:
        # Fetch a chunk of klines (up to 1000)
        print(
            f"Fetching klines for {symbol} ending at {datetime.fromtimestamp(end_time_ms / 1000)}"
        )
        response = session.get_kline(
            category="spot",
            symbol=symbol,
            interval=interval,
            end=end_time_ms,
            limit=1000,
        )

        if response.get("retCode") == 0 and response.get("result", {}).get("list"):
            klines = response["result"]["list"]
            # Bybit returns newest first, so the oldest is at the end of the list
            oldest_kline_time = int(klines[-1][0])

            # Filter out klines that are older than our required start time
            klines_in_range = [k for k in klines if int(k[0]) >= start_time_ms]
            all_klines.extend(klines_in_range)

            # If the oldest kline in the chunk is before our start time, we're done
            if oldest_kline_time < start_time_ms or len(klines) < 1000:
                break

            # Set the end time for the next chunk to be the timestamp of the oldest kline we just received
            end_time_ms = oldest_kline_time
        else:
            # Log the error response from ByBit and break the loop
            print(f"ByBit API returned an error or no data. Response: {response}")
            break

        # Respect Bybit's rate limits
        time.sleep(0.2)  # Increased sleep time slightly for safety

    # Sort the combined list by timestamp in ascending order (oldest to newest)
    return sorted(all_klines, key=lambda k: int(k[0]))
