import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def generate_trade_chart(klines: list, trade_history: dict) -> io.BytesIO:
    """
    Generates a chart from kline and trade history data.

    :param klines: List of kline data from ByBit.
    :param trade_history: Dictionary with 'buy_actions' and 'sell_actions'.
    :return: A BytesIO buffer containing the PNG image.
    """
    if not klines:
        return io.BytesIO()  # Return empty buffer if no kline data

    # Create a lookup map for kline data: timestamp -> [low, high]
    kline_map = {int(k[0]): {"low": float(k[3]), "high": float(k[4])} for k in klines}
    kline_timestamps = sorted(kline_map.keys())

    # Extract data for plotting the main price line
    timestamps = [datetime.fromtimestamp(ts / 1000) for ts in kline_timestamps]
    close_prices = [
        kline_map[ts]["high"] for ts in kline_timestamps
    ]  # Using high for line plot

    # --- Helper function to find the corresponding kline for a trade ---
    def get_trade_y_position(trade_datetime_str, trade_type):
        trade_dt = datetime.strptime(trade_datetime_str, "%Y-%m-%d %H:%M:%S")
        trade_ts = int(trade_dt.timestamp() * 1000)

        # Find the kline that contains this trade
        # We do this by finding the last kline that started before or at the same time as the trade
        # Note: This assumes kline_timestamps is sorted
        target_kline_ts = None
        for i, kts in enumerate(kline_timestamps):
            if kts <= trade_ts:
                if i + 1 < len(kline_timestamps):
                    if kline_timestamps[i + 1] > trade_ts:
                        target_kline_ts = kts
                        break
                else:  # Last kline
                    target_kline_ts = kts
                    break

        if target_kline_ts is None:
            return None, None

        kline_data = kline_map[target_kline_ts]
        price_range = max(close_prices) - min(close_prices)
        offset = price_range * 0.03  # 3% of price range for offset

        if trade_type == "buy":
            return trade_dt, kline_data["low"] - offset
        else:  # sell
            return trade_dt, kline_data["high"] + offset

    # --- Process trades to get their plot positions ---
    buy_times, buy_y = [], []
    sell_times, sell_y = [], []

    valid_buys = [
        t
        for t in trade_history.get("buy_actions", [])
        if isinstance(t, dict) and "price" in t and "datetime" in t
    ]
    for trade in valid_buys:
        dt, y = get_trade_y_position(trade["datetime"], "buy")
        if dt:
            buy_times.append(dt)
            buy_y.append(y)

    valid_sells = [
        t
        for t in trade_history.get("sell_actions", [])
        if isinstance(t, dict) and "price" in t and "datetime" in t
    ]
    for trade in valid_sells:
        dt, y = get_trade_y_position(trade["datetime"], "sell")
        if dt:
            sell_times.append(dt)
            sell_y.append(y)

    # --- Create the plot ---
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(15, 8))

    # Plot price history
    ax.plot(timestamps, close_prices, label="Price", color="cyan", linewidth=1)

    # Plot buy and sell markers
    ax.scatter(
        buy_times, buy_y, label="Buys", marker="^", color="lime", s=100, zorder=5
    )
    ax.scatter(
        sell_times, sell_y, label="Sells", marker="v", color="red", s=100, zorder=5
    )

    # Formatting
    ax.set_title("Trade History", fontsize=20)
    ax.set_ylabel("Price (USDT)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.3)
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))

    # Save plot to a memory buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return buf
