# src/__main__.py
# Graggle bot: Discord bot for personal use in my discord server
# Copyright (C) 2026  Liam Kelly
from discord import ApplicationContext, Bot

import src.logs  # noqa: F401
from src.utils.config import DISCORD_TOKEN

bot = Bot()

bot.load_extension("src.cogs.website_check")
bot.load_extension("src.cogs.rcon")

@bot.slash_command()
async def foo(ctx: ApplicationContext) -> None:
    await ctx.respond("bar")

bot.run(DISCORD_TOKEN)
