import discord
from discord.ext import commands
from discord import app_commands
from django.utils import timezone

from bot.models import User, Submission, Challenge, Vote
from creatives_discord_bot.settings import SUBMISSIONS_CHANNEL, GUILD_ID


class Submissions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @property
    def submissions_channel(self):
        return self.bot.get_channel(SUBMISSIONS_CHANNEL)

    @app_commands.command(description='Submit your work for the current challenge')
    async def submit(self, interaction: discord.Interaction, attachment: discord.Attachment, description: str):
        author = await User.objects.get_async(discord_id=interaction.user.id)

        await interaction.response.send_message(
            f'Hello {author.display_name}. Thank you for the submission! '
            f'It will be posted in <#{SUBMISSIONS_CHANNEL}> soon.',
            ephemeral=True
        )

        now = timezone.now()
        challenge = await Challenge.objects.get_async(start__lte=now, deadline__gt=now)

        submission = await Submission.objects.create_async(
            author=author,
            challenge=challenge,
            description=description,
            file_url=attachment.url,
            media_type=attachment.content_type
        )

        message: discord.Message = await self.submissions_channel.send(
            f'Submission by {interaction.user.mention} for **{challenge.title}** challenge\n'
            f'> {description}',
            file=await attachment.to_file()
        )

        submission.message_id = message.id
        await submission.save_async()

        emoji = '\N{THUMBS UP SIGN}'
        await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        author: discord.Member = payload.member
        if payload.channel_id != SUBMISSIONS_CHANNEL and author.id != self.bot.user.id:
            return

        user = await User.objects.get_async(discord_id=author.id)
        submission = await Submission.objects.get_async(message_id=payload.message_id)

        if user.pk != submission.author_id:
            await Vote.objects.get_or_create_async(
                user=user,
                submission=submission
            )


async def setup(bot):
    await bot.add_cog(Submissions(bot), guild=discord.Object(id=GUILD_ID))

