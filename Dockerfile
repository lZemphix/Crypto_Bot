FROM python:3.13.2
WORKDIR /bot
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
ENTRYPOINT [ "python3", "src/main.py"]
