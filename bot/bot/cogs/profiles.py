import discord
from discord import app_commands
from discord.ext import commands
from django.urls import reverse

from bot.models import User
from creatives_discord_bot.settings import GENERAL_CHANNEL, GUILD_ID, BASE_URL


class Profiles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def get_embed_with_profile(user: User):
        profile_url = BASE_URL + reverse('profile', kwargs={'user_id': user.discord_id})

        embed = discord.Embed(
            description=f'Check out your profile on [creatives-discord.space]({profile_url})'
        )
        embed.add_field(name='Lives', value=user.get_lives_string(), inline=True)
        embed.add_field(name='Submissions ', value=f'{await user.submission_set.acount()}', inline=True)
        embed.set_image(url=user.avatar_url)
        return embed

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        user, created = await User.objects.aget_or_create(
            discord_id=member.id,
            defaults={
                'display_name': member.display_name,
                'avatar_url': member.display_avatar.url if member.display_avatar else None,
            }
        )

        await self.bot.get_channel(GENERAL_CHANNEL).send(
            f'Hello {user.mention}. Wellcome!',
            embed=await self.get_embed_with_profile(user)
        )

    @commands.Cog.listener()
    async def on_member_update(self, old_member: discord.Member, member: discord.Member):
        await User.objects.aupdate_or_create(
            discord_id=member.id,
            defaults={
                'display_name': member.display_name,
                'avatar_url': member.display_avatar.url if member.display_avatar else None,
            }
        )

    @app_commands.command(description='Register yourself (in case bot does not know about you)')
    async def register_me(self, interaction: discord.Interaction):
        member = interaction.user
        user, created = await User.objects.aget_or_create(
            discord_id=member.id,
            defaults={
                'display_name': member.display_name,
                'avatar_url': member.display_avatar.url if member.display_avatar else None,
            }
        )
        if created:
            await interaction.response.send_message(f'Hello {user.mention}. ',
                                                    ephemeral=True,
                                                    embed=await self.get_embed_with_profile(user))
        else:
            await interaction.response.send_message(f'Hello {user.mention}. '
                                                    f'No worries. I know you already. ',
                                                    ephemeral=True,
                                                    embed=await self.get_embed_with_profile(user))


async def setup(bot):
    await bot.add_cog(Profiles(bot), guild=discord.Object(id=GUILD_ID))
