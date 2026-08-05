# src/logs.py
from logging import (
    DEBUG,
    INFO,
    FileHandler,
    Formatter,
    StreamHandler,
    basicConfig,
)
from sys import stdout

from src.utils.config import DEBUG_LOGS, LOG_LOCATION

formatter = Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")

file_handler = FileHandler(filename=LOG_LOCATION, encoding="utf-8", mode="w")
file_handler.setFormatter(formatter)

stream_handler = StreamHandler(stdout)
stream_handler.setFormatter(formatter)

level = INFO
if DEBUG_LOGS:
    level = DEBUG

basicConfig(level=level, handlers=[file_handler, stream_handler])
