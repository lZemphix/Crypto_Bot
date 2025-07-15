FROM python:3.13.2-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends

RUN pip3 install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN python3 -m poetry config virtualenvs.create false \
    && python3 -m poetry install --no-interaction --no-ansi --no-root

COPY . .

ENTRYPOINT ["python3", "src/main.py"]