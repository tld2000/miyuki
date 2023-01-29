import os
import discord
from discord.ext import tasks, commands


class Client(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=["!"],
            intents=discord.Intents.all(),
            help_command=commands.DefaultHelpCommand(dm_help=True)
        )

    async def setup_hook(self):  # overwriting a handler
        print(f"\033[31mLogged in as {client.user}\033[39m")
        cogs_folder = f"{os.path.abspath(os.path.dirname(__file__))}/cogs"
        for filename in os.listdir(cogs_folder):
            if filename.endswith(".py"):
                await client.load_extension(f"cogs.{filename[:-3]}")
        # await client.tree.sync()
        print("Loaded cogs")


client = Client()
client.run(os.getenv('DISCORD_TOKEN'))