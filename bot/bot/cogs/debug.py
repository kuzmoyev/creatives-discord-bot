import sys
import traceback

import discord
from discord import app_commands
from discord.ext import commands

from creatives_discord_bot.settings import BOT_ALERTS_CHANNEL, DEBUG, GUILD_ID


class DebugDev(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user} (DEBUG)')

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        traceback.print_exception(*sys.exc_info(), file=sys.stderr)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


class DebugProd(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        @self.bot.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            await self.alert_channel.send(
                f'Error while processing slash command `/{interaction.command.name}` '
                f'by {interaction.user.mention} in <#{interaction.channel_id}>\n'
                f'```{"".join(traceback.format_tb(error.__traceback__))}```\n'
                f'Original error:\n'
                f'```{"".join(traceback.format_tb(error.original.__traceback__))}```'
            )

    @property
    def alert_channel(self):
        return self.bot.get_channel(BOT_ALERTS_CHANNEL)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user}')

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        await self.alert_channel.send(
            f'Error while processing `{event}`\n'
            f'Args:```{args}```\n'
            f'Kwargs:```{kwargs}```\n'
            f'```{traceback.format_exc()}```'
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await self.alert_channel.send(
            f'Error while processing `{ctx.invoked_with}`\n'
            f'```{"".join(traceback.format_tb(error.__traceback__))}```'
        )

    @app_commands.command(description='Test alert system')
    @commands.is_owner()
    async def test_alert(self, interaction: discord.Interaction):
        await interaction.response.send_message("Testing alert system!", ephemeral=True)
        raise Exception('Testing alert system')

    @app_commands.command(description='Ping')
    @commands.is_owner()
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hey, I'm here!", ephemeral=True)


async def setup(bot):
    if DEBUG:
        await bot.add_cog(DebugDev(bot))
    else:
        await bot.add_cog(DebugProd(bot), guild=discord.Object(id=GUILD_ID))
