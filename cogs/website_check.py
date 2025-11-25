import discord, config, aiohttp
from discord.ext import commands, tasks
from discord import app_commands

# Main class for checking website status'
class WebsiteCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.website_check, guilds=self.bot.active_guilds)

        self.bot.console_log('WebsiteCheck cog loaded successfully.')

        self.silent = False
        self.silent = config.get_dynamic_config('website_check_silent')

        self.websites = {}
        self.websites = config.get_dynamic_config('websites')

    # Listen for bot ready event to start website check loop
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_websites.is_running():
            self.check_websites.start()

    # Loop task to periodically get http status code from websites
    @tasks.loop(seconds=config.WEBSITE_CHECK_INTERVAL)
    async def check_websites(self):
        websites = self.websites
        if not websites: return
        for url in websites.keys():
            host = url if url.startswith('https') else f'https://{url}'
            notif_channel = self.bot.get_channel(websites[url][0])
            status = None

            # Make request to website for status code
            async with aiohttp.ClientSession() as session:
                async with session.head(host) as response:
                    status = response.status
            
            # Send notification if status has changed from False to True
            if status == 200:
                if not self.websites[url][1]:
                    if not self.silent:
                        notif_embed = discord.Embed(
                            title = f'✅ {host} Online ✅',
                            timestamp = discord.utils.utcnow()
                        )
                        notif_embed.set_footer(text=f'returned {status}')
                        notif_embed.set_image(url='https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ21sYTZlZXdmNW9tNGFjcGxrd2MwbXhsZTJ1OWE2ODM2Nml6azdpNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/wypKXPQggwaCA/giphy.gif')

                        await notif_channel.send(embed=notif_embed)
                    self.websites[url][1] = True
            
            # Send notification if status has changed from True to False
            else:
                if self.websites[url][1]:
                    if not self.silent:
                        notif_embed = discord.Embed(
                            title = f'🚨 {host} Offline 🚨',
                            timestamp = discord.utils.utcnow()
                        )
                        notif_embed.set_footer(text=f'returned {status}')
                        notif_embed.set_image(url='https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3pwZ2NmYTJ4dzNrMDdodzRjeHByZXFtcG02bmE0aDIxOXZnMTZvYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/AmT7Raa4GJQsM/giphy.gif')

                        await notif_channel.send(embed=notif_embed)
                    self.websites[url][1] = False
        config.set_dynamic_config('websites', self.websites)

    # Run before website check loop to check if loop running already on discord
    @check_websites.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    # Run after website check loop to save website status to dynamic config
    @check_websites.after_loop
    async def after_check(self):
        config.set_dynamic_config('websites', self.websites)

    # Define website check command group
    website_check = app_commands.Group(
        name='website_check',
        description='Commands for website monitoring'
    )
    
    # Add website command
    @website_check.command(name='add', description='Add website to monitoring list')
    async def add_website(self, interaction: discord.Interaction, url: str, channel: discord.TextChannel):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /website_check add {url} <#{channel.id}>')

        websites = config.get_dynamic_config('websites')
        websites[url] = [channel.id, True]
        config.set_dynamic_config('websites', websites)

        self.websites = websites

        await interaction.response.send_message(f'Added `{url}` to website monitoring list, notifications will be sent to <#{channel.id}>.', ephemeral=True)
    
    # Remove website command
    @website_check.command(name='remove', description='Removes a website from the monitoring list')
    async def remove_website(self, interaction: discord.Interaction, url: str):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /website_check remove {url}')
        
        websites = config.get_dynamic_config('websites')
        del websites[url]
        config.set_dynamic_config('websites', websites)

        self.websites = websites

        await interaction.response.send_message(f'Removed `{url}` from website monitoring list.', ephemeral=True)
    
    # List websites command
    @website_check.command(name='list', description='Lists all monitored websites')
    async def list_website(self, interaction: discord.Interaction):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /website_check list')

        out = []
        for site in self.websites.keys():
            status = 'Online' if self.websites[site][1] else 'Offline'
            out.append(f'`{site}` is currently **{status}**.')
        
        if out:
            await interaction.response.send_message('\n'.join(out), ephemeral=True) 
        else:
            await interaction.response.send_message('No currently monitored websites.', ephemeral=True)

    # Toggle silent command
    @website_check.command(name='silent', description='Toggles silent website checks')
    async def toggle_silent(self, interaction: discord.Interaction):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /website_check silent')

        config_value = config.get_dynamic_config('website_check_silent')
        new_value = False if config_value else True
        config.set_dynamic_config('website_check_silent', new_value)
        self.silent = new_value

        await interaction.response.send_message(f'Set silent to `{new_value}`.', ephemeral=True)

# Setup function to load cog into bot
async def setup(bot):
    await bot.add_cog(WebsiteCheck(bot))
