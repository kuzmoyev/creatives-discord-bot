from urllib.parse import urljoin

import discord
from discord.ext import commands
from discord import app_commands, Embed, ui

from bot.models import User, Submission, Challenge, Vote
from creatives_discord_bot.settings import SUBMISSIONS_CHANNEL, GUILD_ID, DISCORD_SUBMISSION_URL


class ConfirmationModal(ui.Modal, title='Delete submission'):
    answer = ui.TextInput(label='Do you want to delete your submission?', placeholder='yes/no', max_length=3)

    def __init__(self, submission: Submission, challenge: Challenge, submissions_channel: discord.TextChannel):
        super().__init__()
        self.submission = submission
        self.challenge = challenge
        self.submissions_channel = submissions_channel

    async def on_submit(self, interaction: discord.Interaction):
        if self.answer.value.lower() == 'yes':

            msg = await self.submissions_channel.fetch_message(self.submission.message_id)
            await msg.delete()

            await self.submission.adelete()
            await interaction.response.send_message(
                f'Your submission for **{self.challenge.title}** challenge has been deleted!\n'
                f'You can submit a new one!',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"No worries, I'll keep it.",
                ephemeral=True
            )


class Submissions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description='Submit your work for the current challenge')
    async def submit(
            self,
            interaction: discord.Interaction,
            attachment: discord.Attachment,
            description: str
    ):
        author: User = await User.objects.aget(discord_id=interaction.user.id)
        try:
            challenge = await Challenge.aget_current()
        except Challenge.NoCurrentChallenge:
            await interaction.response.send_message(
                f"Hello {author.mention}. "
                f"There's no active challenge at the moment.\n"
                f"Here's the description, you've just sent, so you don't loose it :wink: :\n"
                f"> {description}",
                ephemeral=True
            )
            return

        try:
            submission = await Submission.objects.aget(author=author, challenge=challenge)
            await interaction.response.send_message(
                f"Hello {author.mention}. "
                f"You have already submitted your work for the current challenge!\n"
                f"Check it here {urljoin(DISCORD_SUBMISSION_URL, str(submission.message_id))}\n"
                f"If you want to edit it, try `/edit_submission` command.\n"
                f"Here's the description, you've just sent, so you don't loose it :wink: :\n"
                f"> {description}",
                ephemeral=True
            )
            return
        except Submission.DoesNotExist:
            # then create
            pass

        submissions_count = await author.submission_set.acount()
        if submissions_count == 0:
            await interaction.response.send_message(
                f'Hello {author.mention}. Congrats on your first submission! '
                f'It will be posted in <#{SUBMISSIONS_CHANNEL}> soon.',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'Hello {author.mention}. Thank you for the submission! '
                f'It will be posted in <#{SUBMISSIONS_CHANNEL}> soon.',
                ephemeral=True
            )

        submission = await Submission.objects.acreate(
            author=author,
            challenge=challenge,
            description=description,
            file_url=attachment.url,
            media_type=attachment.content_type
        )

        embed = await self._build_submission_embed(submission)

        message: discord.Message = await self.submissions_channel.send(
            file=await attachment.to_file(),
            embed=embed
        )

        received_attachment = message.attachments[0]
        submission.file_url = received_attachment.url
        submission.media_type = received_attachment.content_type

        submission.message_id = message.id

        await submission.asave()

        emoji = '\N{THUMBS UP SIGN}'
        await message.add_reaction(emoji)

    @app_commands.command(description='Edit your submission for the current challenge and/or its description')
    async def edit_submission(
            self,
            interaction: discord.Interaction,
            attachment: discord.Attachment = None,
            description: str = None
    ):
        author: User = await User.objects.aget(discord_id=interaction.user.id)
        if description:
            description_string = f"\nHere's the description, you've just sent, so you don't loose it :wink: :\n" \
                                 f"> {description}"
        else:
            description_string = ""

        try:
            challenge = await Challenge.aget_current()
        except Challenge.NoCurrentChallenge:
            await interaction.response.send_message(
                f"Hello {author.mention}. "
                f"There's no active challenge at the moment.\n"
                f"You can not edit your submissions for the finished challenges." + description_string,
                ephemeral=True
            )
            return

        try:
            submission = await Submission.objects.aget(author=author, challenge=challenge)
        except Submission.DoesNotExist:
            await interaction.response.send_message(
                f"Hello {author.mention}. "
                f"You haven't yet submitted your work for the current challenge. Use `/submit` to do so.\n"
                f"You can not edit your submissions for the finished challenges." + description_string,
                ephemeral=True
            )
            return

        if not attachment and not description:
            await interaction.response.send_message(
                f"Hello {author.mention}. "
                f"You have to add `attachment` and/or `description` to update your submission.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f'Hello {author.mention}. I will update your submission for the **{challenge.title}** challenge.',
            ephemeral=True
        )

        if description:
            submission.description = description

        message = await self.submissions_channel.fetch_message(submission.message_id)
        embed = await self._build_submission_embed(submission)
        attachments_to_send = [await attachment.to_file()] if attachment else message.attachments
        message = await message.edit(attachments=attachments_to_send, embed=embed)

        if attachment:
            received_attachment = message.attachments[0]
            submission.file_url = received_attachment.url
            submission.media_type = received_attachment.content_type

        await submission.asave()

    @app_commands.command(description='Delete your submission for the current challenge. '
                                      'Note: you can use `/edit_submission` to edit it.')
    async def delete_submission(
            self,
            interaction: discord.Interaction,
    ):
        author: User = await User.objects.aget(discord_id=interaction.user.id)

        try:
            challenge = await Challenge.aget_current()
        except Challenge.NoCurrentChallenge:
            await interaction.response.send_message(
                f"Hello {author.mention}. "
                f"There's no active challenge at the moment.\n"
                f"You can not delete your submissions for the finished challenges.",
                ephemeral=True
            )
            return

        try:
            submission = await Submission.objects.aget(author=author, challenge=challenge)
        except Submission.DoesNotExist:
            await interaction.response.send_message(
                f"Hello {author.mention}. "
                f"You haven't yet submitted your work for the current challenge. Use `/submit` to do so.\n"
                f"You can not delete your submissions for the finished challenges.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(ConfirmationModal(submission, challenge, self.submissions_channel))

    @commands.Cog.listener()
    async def on_raw_reaction_add(
            self,
            payload: discord.RawReactionActionEvent
    ):
        author_id = payload.user_id
        if payload.channel_id != SUBMISSIONS_CHANNEL or author_id == self.bot.user.id:
            return

        author = await User.objects.aget(discord_id=author_id)
        submission = await Submission.objects.aget(message_id=payload.message_id)

        if author.pk != submission.author_id:
            created, vote = await Vote.objects.aget_or_create(
                user=author,
                submission=submission
            )

            if created:
                message = await self.submissions_channel.fetch_message(submission.message_id)
                embed = await self._build_submission_embed(submission)
                await message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
            self,
            payload: discord.RawReactionActionEvent
    ):
        author_id = payload.user_id
        if payload.channel_id != SUBMISSIONS_CHANNEL or author_id == self.bot.user.id:
            return

        author = await User.objects.aget(discord_id=author_id)
        submission = await Submission.objects.aget(message_id=payload.message_id)
        message = await self.submissions_channel.fetch_message(submission.message_id)

        reacted_users_ids = {user.id for reaction in message.reactions async for user in reaction.users()}
        if author.pk != submission.author_id and author_id not in reacted_users_ids:
            try:
                vote = await Vote.objects.aget(
                    user=author,
                    submission=submission
                )

                await vote.adelete()

                embed = await self._build_submission_embed(submission)
                await message.edit(embed=embed)
            except Vote.DoesNotExist:
                pass

    @property
    def submissions_channel(self) -> discord.TextChannel:
        return self.bot.get_channel(SUBMISSIONS_CHANNEL)

    @staticmethod
    async def _build_submission_embed(submission: Submission):
        author = await User.objects.aget(pk=submission.author_id)
        challenge = await Challenge.objects.aget(pk=submission.challenge_id)

        embed = Embed(
            description=submission.description
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        embed.add_field(name='Challenge', value=challenge.title, inline=False)
        embed.add_field(name='Author', value=author.mention)
        embed.add_field(name='Points', value=f'+{await submission.aget_score()}')
        return embed


async def setup(bot):
    await bot.add_cog(Submissions(bot), guild=discord.Object(id=GUILD_ID))
