from logging import FileHandler, StreamHandler, basicConfig
import logging


def load_logger_config(level: int = 10):
    DATE_FMT = "%Y-%m-%d %H:%M:%S"
    FORMAT = (
        "%(asctime)s : %(module)-15s : %(lineno)-4s : %(levelname)-8s : %(message)s"
    )
    file = FileHandler("logs.log", mode="a")
    console = StreamHandler()

    basicConfig(level=level, format=FORMAT, datefmt=DATE_FMT, handlers=[file, console])

    logging.getLogger("urllib3").setLevel(30)
    logging.getLogger("requests").setLevel(30)
    logging.getLogger("_http_manager").setLevel(30)
