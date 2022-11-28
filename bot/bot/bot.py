import os
import logging

import discord
from discord.ext import commands

from creatives_discord_bot import settings
from creatives_discord_bot.settings import DISCORD_TOKEN, GUILD_ID

COGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cogs')


class Bot(commands.Bot):
    async def setup_hook(self):
        print('Loading extensions...')
        for filename in os.listdir(COGS_DIR):
            if filename.endswith('.py'):
                cog_module = filename[:-3]
                await self.load_extension(f'bot.bot.cogs.{cog_module}')
                print('\t', cog_module, 'loaded')

        print('Syncing...')
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        print('Synced')


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = Bot(command_prefix='!', intents=intents)

    if settings.DEBUG:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
    else:
        handler = None
    bot.run(DISCORD_TOKEN, log_handler=handler)
