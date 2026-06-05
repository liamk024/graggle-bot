# Graggle bot: Discord bot for personal use in my discord server
# Copyright (C) 2026  Liam Kelly

from discord import ApplicationContext, Bot

from .utils.config import DISCORD_TOKEN, GUILD_ID

bot = Bot()

bot.load_extension(f"{__package__}.cogs.website_check")

@bot.slash_command(guild_ids=GUILD_ID)
async def foo(ctx: ApplicationContext) -> None:
    await ctx.respond("bar")

def main() -> None:
    bot.run(DISCORD_TOKEN)
