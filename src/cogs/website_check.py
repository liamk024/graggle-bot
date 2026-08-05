# src/cogs/website_check.py
import logging
from asyncio import gather
from datetime import datetime
from zoneinfo import ZoneInfo

from discord import (
    ApplicationContext,
    Bot,
    Embed,
    SlashCommandGroup,
    TextChannel,
    option,
)
from discord.ext import commands, tasks

from src.models.schemas import Website
from src.utils.autocomplete import website_autocomplete
from src.utils.config import DOWN_EMBED_URL, GUILD_ID, TZ_INFO, UP_EMBED_URL
from src.utils.queries import (
    delete_website,
    get_all_websites,
    get_option,
    set_option,
    set_website,
)
from src.utils.utility import build_status_embed, check_website

logger = logging.getLogger(__name__)

class WebsiteCheck(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.loop_prev = True
        self.silent_notif = False

        silent_saved = get_option("web_silent")
        if silent_saved:
            self.silent_notif = silent_saved.enable

        self.check_loop.start()

    web = SlashCommandGroup("web", "Website checking utilities", guild_ids=GUILD_ID)

    # simply pings a website to check for response code
    @web.command(name="ping", description="Ping a website to check if it's up")
    @option("url", str, description="URL to check, beginning with http:// or https://")
    async def ping(self, ctx: ApplicationContext, url: str) -> None:
        await ctx.defer()

        status: int | None = await check_website(url)

        response: str = "An error has occurred"
        if status:
            if (200 <= status < 400):
                response = f"Success with code {status}"
            else:
                response = f"Failed with code {status}"

        logger.info(f"'{ctx.author.name}': Pinged website {url} and got {response.lower()}")
        await ctx.respond(response)

    # turns on or off suppression of notifications
    @web.command(name="silent", description="Toggle suppression of web notifications")
    @option("enable", bool, description="Whether or not notifications should be suppressed")
    async def silent(self, ctx: ApplicationContext, enable: bool) -> None:
        if set_option("web_silent", enable):
            self.silent_notif = enable
            logger.info(f"'{ctx.author.name}': Set web_silent to '{enable}'")
            await ctx.respond(f"Set `web_silent` to `{enable}`", ephemeral=True)
            return
        logger.error(f"'{ctx.author.name}': Failed to set web_silent to '{enable}'")
        await ctx.respond("Failed to set option `web_silent`", ephemeral=True)

    # adds a site as a tracked object
    @web.command(name="track", description="Add a site to the list of tracked sites")
    @option("url", str, description="URL to track, beginning with http:// or https://")
    @option("channel", TextChannel, description="Where to post updates about this site")
    @option("up_embed_url", str, description="Link to the embedded image or gif displayed when the site comes back up", default = UP_EMBED_URL)
    @option("down_embed_url", str, description="Link to the embedded image or gif displayed when the site goes down", default = DOWN_EMBED_URL)
    async def track(self, ctx: ApplicationContext, url: str, channel: TextChannel, up_embed_url: str, down_embed_url: str) -> None:
        site: Website = Website(
            url = url,
            last_change = datetime.now(ZoneInfo(TZ_INFO)),
            last_check = datetime.now(ZoneInfo(TZ_INFO)),
            announcement_channel = channel.id,
            up_embed_url = up_embed_url,
            down_embed_url = down_embed_url,
        )

        if set_website(site):
            response: str = f"Now tracking '{url}' in {channel.mention}"
            logger.info(f"'{ctx.author.name}': {response}")
            await ctx.respond(response)
        else:
            response: str = f"Failed to add '{url}' to tracking list"
            logger.error(f"'{ctx.author.name}': {response}")
            await ctx.respond(response)

    # removes a site from the tracking list
    @web.command(name="untrack", description="Remove a site from the list of tracked sites")
    @option("url", str, description="URL to remove, beginning with http:// or https://", autocomplete=website_autocomplete)
    async def untrack(self, ctx: ApplicationContext, url: str) -> None:
        if delete_website(url):
            response: str = f"Removed '{url}' from tracking list"
            logger.info(f"'{ctx.author.name}': {response}")
            await ctx.respond(response)
        else:
            response: str = f"Failed to remove '{url}' from tracking list"
            logger.error(f"'{ctx.author.name}': {response}")
            await ctx.respond(response)

    # output list of tracked sites and their statuses
    @web.command(name="list", description="Lists status of all tracked sites")
    async def list(self, ctx: ApplicationContext) -> None:
        websites: list[Website] | None = get_all_websites()
        logger.info(f"'{ctx.author.name}': Requested tracked website list")

        if websites:
            site_list = "\n".join(
                f"✅ `{site.url}` is **Online**"
                if (200 <= site.status < 400) else
                f"❌ `{site.url}` is **Offline**: could not reach server"
                if (site.status == 599) else
                f"❌ `{site.url}` is **Offline**: code {site.status}"
                for site in websites
            )
            await ctx.respond(site_list)
            return

        logger.debug(f"'{ctx.author.name}': Requested tracked website list but list is empty")
        await ctx.respond("There are no tracked sites")

    # handles the check and notification logic for a single site
    async def _check_site(self, site: Website) -> None:
        # defaults to status 599 if an error occurs
        status: int = await check_website(site.url) or 599

        if status == site.status:
            # no status change, just update last_check timestamp
            site_model = Website(
                url = site.url,
                status = site.status,
                last_change = site.last_change,
                last_check = datetime.now(ZoneInfo(TZ_INFO)),
                announcement_channel = site.announcement_channel,
                up_embed_url = site.up_embed_url,
                down_embed_url = site.down_embed_url,
            )
            logger.debug(f"No change to website '{site.url}' status")
            set_website(site_model)
            return

        # status has changed, update with new status and change timestamp
        site_model = Website(
            url = site.url,
            status = status,
            last_change = datetime.now(ZoneInfo(TZ_INFO)),
            last_check = datetime.now(ZoneInfo(TZ_INFO)),
            announcement_channel = site.announcement_channel,
            up_embed_url = site.up_embed_url,
            down_embed_url = site.down_embed_url,
        )
        logger.info(f"Site '{site.url}' status has changed from '{site.status}' to '{status}'")
        set_website(site_model)

        # build the appropriate notification embed for the status change
        notif_embed: Embed = build_status_embed(site, status)

        channel = self.bot.get_channel(site.announcement_channel)

        # TODO: implement correct error logging for invalid channel
        if not isinstance(channel, TextChannel):
            logger.error(f"Invalid announcement channel {site.announcement_channel} for {site.url}")
            return

        if not self.silent_notif:
            await channel.send(embed=notif_embed)

    # iterates through tracked sites to check for change in status
    @tasks.loop(seconds=15)
    async def check_loop(self) -> None:
        websites: list[Website] = get_all_websites() or []
        # check all sites concurrently rather than sequentially
        logger.debug("Running website check loop iteration")
        await gather(*[self._check_site(site) for site in websites])

def setup(bot: Bot) -> None:
    bot.add_cog(WebsiteCheck(bot))
    logger.info("Website Check cog loaded")
