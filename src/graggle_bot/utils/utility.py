import logging
from asyncio import sleep as async_sleep
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from discord import Embed
from httpx import AsyncClient, HTTPError, Response

from graggle_bot.models.schemas import Website
from graggle_bot.utils.config import TZ_INFO

logger = logging.getLogger(__name__)

_client = AsyncClient(timeout=10, follow_redirects=True)

def time_diff_str(start: datetime, end: datetime) -> str:
    diff: timedelta = end - start

    total_seconds = int(diff.total_seconds())
    days: int = diff.days
    hours: int = (total_seconds % 86400) // 3600
    minutes: int = (total_seconds % 3600) // 60
    seconds: int = total_seconds % 60

    return f"{days}d {hours:02}h {minutes:02}m {seconds:02}s"

# Ping website to check for response 200
async def check_website(url: str, retries: int = 3, delay: float = 2.0) -> int | None:
    for attempt in range(retries):
        try:
            response: Response = await _client.get(url)
            logger.debug(f"Got response {response.status_code} from {url}")
            return response.status_code
        except HTTPError as error:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed for {url}: {error}")
            if attempt < retries - 1:
                await async_sleep(delay)
    return None

# builds the notification embed for a site status change
def build_status_embed(site: Website, status: int) -> Embed:
    if 200 <= status < 400:
        # site has come back online, calculate downtime duration
        start: datetime = site.last_change.replace(tzinfo=ZoneInfo(TZ_INFO))
        end: datetime = datetime.now(ZoneInfo(TZ_INFO))
        downtime: str = time_diff_str(start, end)

        embed = Embed(
            title = f"✅ {site.url} Online ✅",
            description = f"Down for: {downtime}",
            timestamp = datetime.now(ZoneInfo(TZ_INFO)),
        )
        embed.set_footer(text=f"returned {status}")
        embed.set_image(url=site.up_embed_url)
    else:
        # site has gone offline
        embed = Embed(
            title = f"🚨 {site.url} Offline 🚨",
            timestamp = datetime.now(ZoneInfo(TZ_INFO)),
        )
        embed.set_footer(text="could not reach server" if status == 599 else f"returned {status}")
        embed.set_image(url=site.down_embed_url)

    return embed
