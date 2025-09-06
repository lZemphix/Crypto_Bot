# CMX Trading Bot

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

CMX is an automated cryptocurrency trading bot designed to work with the ByBit exchange. It features a web-based dashboard for monitoring and is containerized with Docker for easy deployment.

## Overview

The project consists of two main services:
1.  **The Bot (`bot`):** A Python script that continuously runs a trading strategy. It executes buys, averages down positions, and sells based on predefined rules and market indicators.
2.  **The Web Dashboard (`web`):** A FastAPI application that provides a user interface to monitor the bot's performance, view current balances, and see the state of ongoing trades.

The bot uses a strategy of making an initial buy, averaging down the position if the price decreases, and selling when a profit target is met. All actions and critical errors are sent as notifications to a specified Telegram chat.

## Features

- **Automated Trading:** Implements a First Buy -> Averaging -> Sell strategy.
- **Web Dashboard:** A clean interface to monitor bot status, trading pair, balance, and current trade cycle metrics.
- **Trade History Visualization:** Generate and send a chart of historical trades to your Telegram chat.
- **Telegram Notifications:** Receive real-time updates on bot status, executed trades, and errors.
- **Configuration-driven:** Easily configure trading parameters and API credentials.
- **Containerized:** Packaged with Docker and Docker Compose for simple, one-command deployment.
- **Database Logging:** Trade actions are logged in a database for analysis.

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** SQLAlchemy (with SQLite by default), Alembic for migrations
- **Charting:** Matplotlib
- **Notifications:** Telegram API
- **Deployment:** Docker, Docker Compose
- **Dependency Management:** Poetry

## Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd cmx
```

### 2. Configure the Environment

You need to set up two configuration files: `.env` for secrets and `bot_config.json` for the trading strategy.

**A. Environment Variables**

Create a `.env` file by copying the example file:

```bash
cp .env.example .env
```

Now, edit the `.env` file and fill in your credentials:

```ini
# ByBit API Credentials
BYBIT_API_KEY="YOUR_API_KEY"
BYBIT_API_SECRET="YOUR_API_SECRET"
ACCOUNT_TYPE="UNIFIED" # Or "CONTRACT"

# Telegram Bot Credentials
TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"

# Web UI Credentials
LOGIN="admin"
PASSWORD="your_secure_password"
```

**B. Bot Configuration**

Edit the `bot_config.json` file to define the trading strategy:

```json
{
    "symbol": "BTCUSDT",
    "interval": 60,
    "amountBuy": 15,
    "stepBuy": 0.8,
    "stepSell": 0.8,
    "RSI": 35,
    "send_notify": true
}
```
- `symbol`: The trading pair (e.g., `BTCUSDT`).
- `interval`: The k-line interval in minutes.
- `amountBuy`: The amount in USDT for each buy order.
- `stepBuy`: The percentage price drop required to trigger an averaging buy.
- `stepSell`: The percentage price increase required to trigger a sell.
- `RSI`: The RSI value used for the initial buy trigger.
- `send_notify`: Enable or disable Telegram notifications.

### 3. Run with Docker Compose

This is the recommended way to run the application. It builds the images for both the bot and the web app and runs them as containerized services.

```bash
docker compose up --build -d
```

The services will start in the background.
- The **Web Dashboard** will be available at [http://localhost:10605](http://localhost:10605).
- The **Bot** will start its trading loop.

To check the logs of the services:
```bash
# View logs for the bot
docker compose logs -f bot

# View logs for the web app
docker compose logs -f web
```

To stop the services:
```bash
docker compose down
```

## Manual Installation (Without Docker)

If you prefer to run the services directly on your host machine.

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)

### Steps

1.  **Install Dependencies:**
    ```bash
    poetry install
    ```
2.  **Configure Environment:**
    Ensure you have created and configured the `.env` and `bot_config.json` files as described in the Docker setup.

3.  **Run Database Migrations:**
    This will set up the database schema.
    ```bash
    poetry run alembic upgrade head
    ```

4.  **Run the Services:**
    You will need two separate terminals.

    **In terminal 1, run the bot:**
    ```bash
    poetry run python src/main.py
    ```

    **In terminal 2, run the web server:**
    ```bash
    poetry run uvicorn web.main:app --host 0.0.0.0 --port 10605
    ```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.