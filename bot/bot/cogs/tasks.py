from datetime import time
import discord
from discord import app_commands
from discord.ext import commands, tasks
from django.urls import reverse
from django.utils import timezone

from bot.models import Challenge, InspirationImage
from creatives_discord_bot.settings import GUILD_ID, CHALLENGES_CHANNEL, BASE_URL


class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.post_challenge.start()

    def cog_unload(self):
        self.post_challenge.cancel()

    @tasks.loop(time=time(hour=9, tzinfo=timezone.get_default_timezone()))
    async def post_challenge(self):
        challenge = await Challenge.aget_current()
        if timezone.now().date() == challenge.start.date():
            await self._post_current_challenge()

    @post_challenge.before_loop
    async def before_post_challenge(self):
        await self.bot.wait_until_ready()

    @app_commands.command(description='Posts current challenge')
    @commands.is_owner()
    async def post_current_challenge(self, interaction: discord.Interaction):
        await interaction.response.send_message('Posting current challenge', ephemeral=True)
        await self._post_current_challenge()

    async def _post_current_challenge(self, challenge: Challenge = None):
        challenge = challenge or await Challenge.aget_current()

        files = []
        embeds = []
        challenge_url = BASE_URL + reverse('challenge', kwargs={'challenge_id': challenge.id})

        async for image in InspirationImage.objects.filter(challenge=challenge):
            file = discord.File(image.image.url[1:])
            embed = discord.Embed(
                title=f'**{challenge.title}**',
                description=f'*{challenge.description}*',
                url=challenge_url
            ).set_image(url=f"attachment://{file.filename}") \
                .add_field(name='Start', value=challenge.start.strftime('%d %B at %H:%M')) \
                .add_field(name='Deadline', value=challenge.deadline.strftime('%d %B at %H:%M'))

            files.append(file)
            embeds.append(embed)

        order = await Challenge.objects.filter(start__lte=challenge.start).acount()

        message = f'__CHALLENGE #{order}__'

        await self.challenges_channel.send(
            message,
            files=files,
            embeds=embeds
        )

    @property
    def challenges_channel(self):
        return self.bot.get_channel(CHALLENGES_CHANNEL)


async def setup(bot):
    await bot.add_cog(Tasks(bot), guild=discord.Object(id=GUILD_ID))
