import os
import requests
import io


def send_chart_to_telegram(image_buffer: io.BytesIO):
    """
    Sends a chart image to a Telegram chat as an uncompressed document.

    :param image_buffer: The BytesIO buffer containing the PNG image.
    :return: The response from the Telegram API.
    """
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    if not bot_token or not chat_id:
        return {"ok": False, "error": "BOT_TOKEN or CHAT_ID not configured"}

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    image_buffer.seek(0)
    files = {"document": ("chart.png", image_buffer, "image/png")}
    data = {"chat_id": chat_id}

    try:
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": str(e)}
