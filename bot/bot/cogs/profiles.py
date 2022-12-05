import discord
from discord import app_commands
from discord.ext import commands

from bot.models import User
from creatives_discord_bot.settings import GENERAL_CHANNEL, GUILD_ID


class Profiles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        user, created = await User.objects.get_or_create_async(
            discord_id=member.id,
            defaults={
                'display_name': member.display_name,
                'avatar_url': member.display_avatar.url if member.display_avatar else None,
            }
        )

        await self.bot.get_channel(GENERAL_CHANNEL).send(f'Hello {user.display_name}. You have {user.lives} lives.')

    @commands.Cog.listener()
    async def on_member_update(self, old_member: discord.Member, member: discord.Member):
        user, created = await User.objects.update_or_create_async(
            discord_id=member.id,
            defaults={
                'display_name': member.display_name,
                'avatar_url': member.display_avatar.url if member.display_avatar else None,
            }
        )
        await self.bot.get_channel(GENERAL_CHANNEL).send(
            f'Hi, {user.display_name}. '
            f'I\'ve updated your profile. '
            f'You have {user.lives} lives.'
        )

    @app_commands.command(description='Register yourself (in case bot does not know about you)')
    async def register_me(self, interaction: discord.Interaction):
        member = interaction.user
        user, created = await User.objects.get_or_create_async(
            discord_id=member.id,
            defaults={
                'display_name': member.display_name,
                'avatar_url': member.display_avatar.url if member.display_avatar else None,
            }
        )
        if created:
            await interaction.response.send_message(f'Hello {user.display_name}. '
                                                    f'You have {user.lives} lives.', ephemeral=True)
        else:
            await interaction.response.send_message(f'Hello {user.display_name}. '
                                                    f'No worries. I know you already. '
                                                    f'You have {user.lives} lives.', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Profiles(bot), guild=discord.Object(id=GUILD_ID))
