from discord import AutocompleteContext

from graggle_bot.models.schemas import RCONServer, Website
from graggle_bot.utils.queries import get_all_rcon_servers, get_all_websites


async def website_autocomplete(ctx: AutocompleteContext) -> list[str]:
    websites: list[Website] = get_all_websites() or []
    return [site.url for site in websites if ctx.value.lower() in site.url.lower()]

async def rcon_autocomplete(ctx: AutocompleteContext) -> list[str]:
    rcon_servers: list[RCONServer] = get_all_rcon_servers() or []
    return [server.name for server in rcon_servers if ctx.value.lower() in server.name.lower()]
