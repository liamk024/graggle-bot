import logging
from sys import stdout

from graggle_bot.utils.config import LOG_LOCATION

formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")

file_handler = logging.FileHandler(filename=LOG_LOCATION, encoding="utf-8", mode="w")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(stdout)
stream_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])

logging.getLogger("httpx").setLevel(logging.WARNING)
