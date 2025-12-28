import discord, config
from discord.ext import commands
from discord import app_commands
from rcon.source import rcon

# Main class for executing RCON commands
class MinecraftRCON(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.minecraft_rcon, guilds=self.bot.active_guilds)

        self.bot.console_log('MinecraftRCON cog loaded successfully.')

    # Define minecraft_rcon command group
    minecraft_rcon = app_commands.Group(
        name='rcon',
        description='Minecraft RCON command bot'
    )
    
    # RCON exec command
    @minecraft_rcon.command(name='exec', description='Executes command on configured Minecraft server through RCON')
    async def rcon_exec(self, interaction: discord.Interaction, cmd: str):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /rcon exec')

        rcon_addr = config.RCON_ADDRESS
        rcon_port = config.RCON_PORT
        rcon_pass = config.RCON_PASSWORD

        response = await rcon(cmd, host=rcon_addr, port=rcon_port, passwd=rcon_pass)
        if not response:
            response = '(no output)'

        await interaction.response.send_message(f'{response}', ephemeral=False)

# Setup function to load cog into bot
async def setup(bot):
    if not (config.RCON_ADDRESS and config.RCON_PASSWORD):
        bot.console_log('No RCON address or RCON password found, not loading minecraft_rcon.')
        return
    else:
        await bot.add_cog(MinecraftRCON(bot))
