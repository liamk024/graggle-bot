import discord, config, aiohttp
from discord.ext import commands
from discord import app_commands
from openai import AsyncOpenAI

# Initialize OpenAI for Async use
openai = AsyncOpenAI()
openai.api_key = config.OPENAI_API_KEY

# Main class for OpenAI response handling
class OpenAIResponse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.openai_response, guilds=self.bot.active_guilds)

        self.bot.console_log('OpenAIResponse cog loaded successfully.')

        current_profile = config.get_dynamic_config('active_prompt_profile')
        profiles = config.get_dynamic_config('prompt_profiles')
        self.prompt = profiles[current_profile]

    # Handle incoming messages
    @commands.Cog.listener()
    async def on_message(self, message):
        # Checks if client is mentioned in message
        if self.bot.user in message.mentions:
            if message.author.bot:
                return

            # Start typing indicator
            async with message.channel.typing():
                input = ""
                # If message is a reply, send only reply as context
                if message.type == discord.MessageType.reply:
                    ref = await message.channel.fetch_message(message.reference.message_id)
                    input = f'Context:\n{ref.author.name}: {ref.content}\n'
                # Else, send last 10 messages as context
                else:
                    prev_msgs = []
                    async for msg in message.channel.history(limit=10, before=message.created_at):
                        prev_msgs.append(msg)
                    prev_msgs.reverse()

                    input = 'Context:\n'
                    for msg in prev_msgs:
                        input = input + f"{msg.author.name}: {msg.content}\n"
                
                input = input + f'Your Prompt:\n{message.author.name}: {message.content}'

                # Generate response from OpenAI
                response = await openai.responses.create(
                    model=config.OPENAI_MODEL,
                    reasoning={'effort': 'minimal'},
                    max_output_tokens=config.MAX_RESPONSE_TOKENS,
                    instructions=self.prompt,
                    input=input
                )

                reply_text = response.output_text

                current_profile = config.get_dynamic_config('active_prompt_profile')
                await message.channel.send(reply_text)
    
    # Define openai_response command group
    openai_response = app_commands.Group(
        name='openai_response',
        description='Commands for editing OpenAI response functionality'
    )
    
    # Add prompt profile command
    @openai_response.command(name='set', description='Sets profile with name <name> to the contents of the linked text file <url>')
    async def set_prompt_profile(self, interaction: discord.Interaction, name: str, url: str):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /openai_response set {name} {url}')

        host = url if url.startswith('https') else f'https://{url}'

        content = ""
        async with aiohttp.ClientSession() as session:
            async with session.get(host) as response:
                content = await response.text()

        profiles = config.get_dynamic_config('prompt_profiles')
        profiles[name] = content
        config.set_dynamic_config('prompt_profiles', profiles)

        current_profile = config.get_dynamic_config('active_prompt_profile')
        profiles = config.get_dynamic_config('prompt_profiles')
        self.prompt = profiles[current_profile]

        await interaction.response.send_message(f'Imported prompt from `{url}` to `{name}`.', ephemeral=True)
    
    # Remove prompt profile command
    @openai_response.command(name='remove', description='Removes profile with name <name>')
    async def remove_prompt_profile(self, interaction: discord.Interaction, name: str):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /openai_response remove {name}')
        
        profiles = config.get_dynamic_config('prompt_profiles')
        if len(profiles.keys()) == 1:
            await interaction.response.send_message(f'Cannot remove last profile.', ephemeral=True)
            return
        
        del profiles[name]
        config.set_dynamic_config('prompt_profiles', profiles)

        current_profile = config.get_dynamic_config('active_prompt_profile')
        if current_profile == name:
            current_profile = profiles.keys()[0]
            config.set_dynamic_config('active_prompt_profile', current_profile)
            self.prompt = profiles[current_profile]
            await interaction.response.send_message(f'Removed `{name}` from prompt profiles. Set current profile to `{current_profile}`.', ephemeral=True)

        await interaction.response.send_message(f'Removed `{name}` from prompt profiles.', ephemeral=True)
    
    # Switch prompt profile command
    @openai_response.command(name='switch', description='Switches active profile')
    async def set_prompt_profile(self, interaction: discord.Interaction, name: str):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /openai_response switch {name}')

        profiles = config.get_dynamic_config('prompt_profiles')
        if name in profiles:
            config.set_dynamic_config('active_prompt_profile', name)
        profiles = config.get_dynamic_config('prompt_profiles')
        self.prompt = profiles[name]

        await interaction.response.send_message(f'Switched active prompt to `{name}`.', ephemeral=True)

    # List prompt profiles command
    @openai_response.command(name='list', description='Lists all prompt profiles')
    async def list_website(self, interaction: discord.Interaction):
        self.bot.console_log(f'\'{interaction.user.name}\' used the command /openai_response list')

        profiles = config.get_dynamic_config('prompt_profiles')

        out = ['Prompt profiles:']
        for profile in profiles.keys():
            out.append(f'`{profile}`')
        await interaction.response.send_message('\n'.join(out), ephemeral=True)

# Setup function to load cog into bot
async def setup(bot):
    await bot.add_cog(OpenAIResponse(bot))
