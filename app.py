# Graggle bot: Discord bot for personal use in my discord server
# Copyright (C) 2026  Liam Kelly
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# main script
import discord, os, config
import discord.ext.commands as commands

# Discord client class
class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents, command_prefix='!')
        self.active_guilds = []

    async def on_ready(self):
        self.console_log(f'Logged on as \'{self.user}\' with ID \'{self.user.id}\'')
        for guild in self.guilds:
            object = discord.Object(id=guild.id)
            self.active_guilds.append(discord.Object(id=guild.id))
            await init_extensions(self)
            result = await self.tree.sync(guild=object)
            self.console_log(f'Successfully synced commands to guild \'{guild.id}\'')
    
    # Helper function for printing to log in correct format
    def console_log(self, event):
        timestamp = discord.utils.utcnow()
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} {event}')

# Load all extensions from cogs directory
async def init_extensions(client):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

# Connect to discord and start tasks
if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)

    client.run(config.DISCORD_TOKEN)
