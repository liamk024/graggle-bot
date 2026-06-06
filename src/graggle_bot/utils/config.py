# src/graggle_bot/utils/config.py
from os import getenv

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN: str | None = getenv("DISCORD_TOKEN")
GUILD_ID: list[int] = [int(getenv("GUILD_ID", "0"))]
TZ_INFO: str = getenv("TZ_INFO", "UTC")
UP_EMBED_URL: str = getenv("UP_EMBED_URL", "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ21sYTZlZXdmNW9tNGFjcGxrd2MwbXhsZTJ1OWE2ODM2Nml6azdpNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/wypKXPQggwaCA/giphy.gif")
DOWN_EMBED_URL: str = getenv("DOWN_EMBED_URL", "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3pwZ2NmYTJ4dzNrMDdodzRjeHByZXFtcG02bmE0aDIxOXZnMTZvYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/AmT7Raa4GJQsM/giphy.gif")
DB_LOCATION: str = getenv("DB_LOCATION", "sqlite:///database.db")
LOG_LOCATION: str = getenv("LOG_LOCATION", "graggle_bot.log")
