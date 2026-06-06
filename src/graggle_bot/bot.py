# Graggle bot: Discord bot for personal use in my discord server
# Copyright (C) 2026  Liam Kelly

from discord import ApplicationContext, Bot

import graggle_bot.logging  # noqa: F401
from graggle_bot.utils.config import DISCORD_TOKEN

bot = Bot()

bot.load_extension("graggle_bot.cogs.website_check")
bot.load_extension("graggle_bot.cogs.rcon")

@bot.slash_command()
async def foo(ctx: ApplicationContext) -> None:
    await ctx.respond("bar")

def main() -> None:
    bot.run(DISCORD_TOKEN)
