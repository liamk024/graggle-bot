# src/cogs/rcon.py
import logging
from io import BytesIO

from discord import (
    ApplicationContext,
    Bot,
    File,
    SlashCommandGroup,
    option,
)
from discord.ext import commands
from rcon.exceptions import (
    ConfigReadError,
    EmptyResponse,
    SessionTimeout,
    UnexpectedTerminator,
    UserAbort,
    WrongPassword,
)
from rcon.source import rcon as rcon_client

from src.models.schemas import RCONServer
from src.utils.autocomplete import rcon_autocomplete
from src.utils.config import GUILD_ID
from src.utils.queries import (
    delete_rcon_server,
    get_all_rcon_servers,
    get_rcon_server,
    set_rcon_server,
)

logger = logging.getLogger(__name__)

# Main class for executing RCON commands
class RCONClient(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    rcon = SlashCommandGroup("rcon", "Source RCON utilities", guild_ids=GUILD_ID)

    # RCON exec command
    @rcon.command(name="exec", description="Executes command on compatible RCON servers using source implementation")
    @option("name", str, description="The name of the remote RCON server to run a command on", autocomplete=rcon_autocomplete)
    @option("command", str, description="The command to execute on the remote RCON server")
    async def exec(self, ctx: ApplicationContext, name: str, command: str) -> None:
        rcon_server: RCONServer | None = get_rcon_server(name)

        if not rcon_server:
            await ctx.respond(f"Could not find RCON server '{name}'")
            return

        try:
            response: str = await rcon_client(command, host=rcon_server.host, port=rcon_server.port, passwd=rcon_server.password)

            if len(response) <= 2000:
                await ctx.respond(response)
            else:
                logger.debug(f"'{ctx.author.name}': RCON response too long, sending as file")
                await ctx.respond(
                    "Response too long, sending as file:",
                    file=File(fp=BytesIO(response.encode()), filename="response.txt")
                )
            logger.info(f"'{ctx.author.name}': Executed command '{command}' on RCON server '{rcon_server.name}'")
            return
        except ConfigReadError:
            response = "Config read error"
            logger.error(f"'{ctx.author.name}': RCON ConfigReadError for server '{rcon_server.name}'")
        except EmptyResponse:
            response = "(no response)"
            logger.debug(f"'{ctx.author.name}': Empty RCON response from server '{rcon_server.name}'")
        except SessionTimeout:
            response = "Session timed out"
            logger.warning(f"'{ctx.author.name}': RCON session timed out for server '{rcon_server.name}'")
        except UserAbort:
            response = "User aborted the connection"
            logger.error(f"'{ctx.author.name}': User aborted RCON session for server '{rcon_server.name}'")
        except WrongPassword:
            response = "Wrong password"
            logger.warning(f"'{ctx.author.name}': Incorrect RCON password for server '{rcon_server.name}'")
        except UnexpectedTerminator:
            response = "Unexpected response from RCON server"
            logger.warning(f"'{ctx.author.name}': Unexpected response from RCON server '{rcon_server.name}'")
        except OSError as e:
            response = "Could not reach RCON server, see logs for details"
            logger.error(f"'{ctx.author.name}': Unexpected error {e} occurred while trying to reach RCON server '{rcon_server.name}' at '{rcon_server.host}:{rcon_server.port}'")
        except Exception as e:
            response = "Unexpected RCON error, see logs for details"
            logger.error(f"'{ctx.author.name}': Unexpected error {e} occurred while trying to reach RCON server '{rcon_server.name}' at '{rcon_server.host}:{rcon_server.port}'")

        await ctx.respond(f"{response}")

    # adds an RCON server
    @rcon.command(name="add", description="Add a remote RCON server")
    @option("name", str, description="The name of the remote RCON server")
    @option("host", str, description="The host IP or domain of the remote RCON server")
    @option("port", int, description="The port of the remote RCON server")
    @option("password", str, description="The password for the remote RCON server")
    async def add(self, ctx: ApplicationContext, name: str, host: str, port: int, password: str) -> None:
        site: RCONServer = RCONServer(
            name = name,
            host = host,
            port = port,
            password = password,
        )

        if set_rcon_server(site):
            response: str = f"Added RCON server '{name}' at '{host}:{port}'"
            logger.info(f"'{ctx.author.name}': {response}")
            await ctx.respond(response)
        else:
            response: str = f"Failed to add RCON server '{name}' at '{host}:{port}'"
            logger.error(f"'{ctx.author.name}': {response}")
            await ctx.respond(response)

    # removes an RCON server
    @rcon.command(name="remove", description="Remove a remote RCON server")
    @option("name", str, description="The name of the remote RCON server to remove", autocomplete=rcon_autocomplete)
    async def remove(self, ctx: ApplicationContext, name: str) -> None:
        if delete_rcon_server(name):
            response: str = f"Removed RCON server '{name}'"
            logger.info(f"'{ctx.author.name}': {response}")
            await ctx.respond(response)
        else:
            response: str = f"Failed to remove RCON server '{name}'"
            logger.error(f"'{ctx.author.name}': {response}")
            await ctx.respond(response)

    # output list of tracked sites and their statuses
    @rcon.command(name="list", description="Lists all RCON servers")
    async def list(self, ctx: ApplicationContext) -> None:
        servers: list[RCONServer] | None = get_all_rcon_servers()
        logger.info(f"'{ctx.author.name}': Requested RCON server list")

        if servers:
            server_list: str = "\n".join(f"- {server.name} {server.host}:{server.port}" for server in servers)

            await ctx.respond(server_list)
            return

        logger.debug(f"'{ctx.author.name}': Requested RCON server list but list is empty")
        await ctx.respond("There are no RCON servers saved")

# Setup function to load cog into bot
def setup(bot: Bot) -> None:
    bot.add_cog(RCONClient(bot))
    logger.info("RCON cog loaded")
