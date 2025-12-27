import discord, rcon, config
from discord.ext import commands
from discord import app_commands

# Main class for rcon interactions
class MinecraftRCON(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.rcon, guilds=self.bot.active_guilds)

        self.bot.console_log('MinecraftRCON cog loaded successfully.')
    
    # Define rcon command group
    rcon = app_commands.Group(
        name='rcon',
        description='Commands for executing RCON commands from Discord.'
    )
    
    # Add prompt profile command
    @rcon.command(name='exec', description='Executes given RCON command ')
    async def exec_command(self, interaction: discord.Interaction, command: str):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /rcon exec {command}')

        

        await interaction.response.send_message(f'Executed command {command} on RCON server {ip}', ephemeral=True)

# Setup function to load cog into bot
async def setup(bot):
    await bot.add_cog(MinecraftRCON(bot))
