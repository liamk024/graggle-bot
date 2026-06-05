# Graggle bot: Discord bot for personal use in my discord server
# Copyright (C) 2026  Liam Kelly

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
from httpx import AsyncClient, HTTPError, Response

from graggle_bot.utils.config import DOWN_EMBED_URL, GUILD_ID, TZ_INFO, UP_EMBED_URL
from graggle_bot.utils.models import Website
from graggle_bot.utils.queries import (
    delete_website,
    get_all_websites,
    get_option,
    set_option,
    set_website,
)
from graggle_bot.utils.utility import time_diff_str


class WebsiteCheck(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.loop_prev = True
        self.silent_notif = False

        silent_saved = get_option("web_silent")
        if silent_saved:
            self.silent_notif = silent_saved.enable

        self.check_loop.start()

    web = SlashCommandGroup("web", "Website checking utilities")

    # Ping website to check for response 200
    async def check_website(self, url: str) -> int | None:
        try:
            async with AsyncClient(timeout=10, follow_redirects=True) as client:
                response: Response = await client.get(url)
            return response.status_code

        except HTTPError as error:
            print(error)

    # simply pings a website to check for response code
    @web.command(name="ping", description="Ping a website to check if it's up", guild_ids=GUILD_ID)
    @option("url", str, description="URL to check, beginning with http:// or https://")
    async def ping(self, ctx: ApplicationContext, url: str) -> None:
        status: int | None = await self.check_website(url)

        response: str = "An error has occurred"
        if status:
            if (200 <= status < 400):
                response = f"Success with code {status}"
            else:
                response = f"Failed with code {status}"

        await ctx.respond(response)

    # turns on or off suppression of notifications
    @web.command(name="silent", description="Toggle suppression of web notifications", guild_ids=GUILD_ID)
    @option("enable", bool, description="Whether or not notifications should be suppressed")
    async def silent(self, ctx: ApplicationContext, enable: bool) -> None:
        if set_option("web_silent", enable):
            self.silent_notif = enable
            await ctx.respond(f"Set `web_silent` to `{enable}`", ephemeral=True)
            return
        await ctx.respond("Failed to set option `web_silent`", ephemeral=True)

    # adds a site as a tracked object
    @web.command(name="track", description="Add a site to the list of tracked sites", guild_ids=GUILD_ID)
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

        response: str = f"Failed to add {url} to tracking list"
        if set_website(site):
            response = f"Now tracking {url} in {channel.mention}"

        await ctx.respond(response)

    # removes a site from the tracking list
    @web.command(name="untrack", description="Remove a site from the list of tracked sites", guild_ids=GUILD_ID)
    @option("url", str, description="URL to remove, beginning with http:// or https://")
    async def untrack(self, ctx: ApplicationContext, url: str) -> None:
        response: str = f"Failed to remove {url} from tracking list"
        if delete_website(url):
            response = f"Removed {url} from tracking list"

        await ctx.respond(response)

    # output list of tracked sites and their statuses
    @web.command(name="list", description="Lists status of all tracked sites")
    async def list(self, ctx: ApplicationContext) -> None:
        websites: list[Website] | None = get_all_websites()
        if websites:
            site_list = "\n".join(
                f"✅ `{site.url}` is **Online**"
                if (site.status == 200) else
                f"❌ `{site.url}` is **Offline** with code {site.status}"
                for site in websites
            )
            await ctx.respond(site_list)
            return

        await ctx.respond("There are no tracked sites")

    # iterates through tracked sites to check for change in status
    @tasks.loop(seconds=15)
    async def check_loop(self) -> None:
        websites: list[Website] = get_all_websites() or []
        for site in websites:
            # defaults to status 599 if an error occurs
            status: int = await self.check_website(site.url) or 599
            if status == site.status:
                site_model = Website(
                    url = site.url,
                    status = site.status,
                    last_change = site.last_change,
                    last_check = datetime.now(ZoneInfo(TZ_INFO)),
                    announcement_channel = site.announcement_channel,
                    up_embed_url = site.up_embed_url,
                    down_embed_url = site.down_embed_url,
                )
            else:
                site_model = Website(
                    url = site.url,
                    status = status,
                    last_change = datetime.now(ZoneInfo(TZ_INFO)),
                    last_check = datetime.now(ZoneInfo(TZ_INFO)),
                    announcement_channel = site.announcement_channel,
                    up_embed_url = site.up_embed_url,
                    down_embed_url = site.down_embed_url,
                )

                # send appropraite notification on status change
                if (200 <= status < 400):
                    start: datetime = site.last_change
                    start = start.replace(tzinfo=ZoneInfo(TZ_INFO))
                    end: datetime = datetime.now(ZoneInfo(TZ_INFO))

                    downtime = time_diff_str(start, end)

                    notif_embed = Embed(
                        title = f"✅ {site.url} Online ✅",
                        description = f"Down for: {downtime}",
                        timestamp = datetime.now(ZoneInfo(TZ_INFO)),
                    )
                    notif_embed.set_footer(text=f"returned {status}")
                    notif_embed.set_image(
                        url=site.up_embed_url
                    )
                else:
                    notif_embed = Embed(
                        title = f"🚨 {site.url} Offline 🚨",
                        timestamp = datetime.now(ZoneInfo(TZ_INFO)),
                    )
                    notif_embed.set_footer(text=f"returned {status}")
                    notif_embed.set_image(
                        url=site.down_embed_url
                    )

                channel = self.bot.get_channel(site.announcement_channel)

                # TODO: implement correct error logging for invalid channel
                if not isinstance(channel, TextChannel):
                    return  # or log error / try fetch_channel fallback

                if not self.silent_notif:
                    await channel.send(embed=notif_embed)
            set_website(site_model)

def setup(bot: Bot) -> None:
    bot.add_cog(WebsiteCheck(bot))
