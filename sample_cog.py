# Graggle bot: Discord bot for personal use in my discord server
# Copyright (C) 2026  Liam Kelly
#
# Full Copyright disclaimer in app.py

import discord, config
from discord.ext import commands
from discord import app_commands

# Main class for checking website status'
class CogTemplate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.cog_template, guilds=self.bot.active_guilds)

        self.bot.console_log('CogTemplate cog loaded successfully.')

    # Define cog_template command group
    cog_template = app_commands.Group(
        name='cog_template',
        description='Template Command'
    )
    
    # Add website command
    @cog_template.command(name='template', description='Template command')
    async def add_website(self, interaction: discord.Interaction, url: str, channel: discord.TextChannel):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /cog_template')

        await interaction.response.send_message(f'Hello, World!', ephemeral=True)

# Setup function to load cog into bot
async def setup(bot):
    await bot.add_cog(Cog(bot))
