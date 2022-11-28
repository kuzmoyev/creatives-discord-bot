from django.db import models
from django.utils.html import format_html

from bot.async_utils import AsyncModel
from creatives_discord_bot.settings import IMAGES_URL


class User(AsyncModel):
    discord_id = models.BigIntegerField(primary_key=True)
    display_name = models.CharField(max_length=256)
    avatar_url = models.URLField(null=True, blank=True)
    registered = models.DateField(auto_now=True)
    lives = models.IntegerField(default=3)

    @property
    def mention(self) -> str:
        return f'<@{self.discord_id}>'

    def __str__(self):
        return f'{self.display_name} ({self.discord_id})'

    def __repr__(self):
        return f'{self.display_name} ({self.discord_id})'


class Challenge(AsyncModel):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    start = models.DateTimeField()
    deadline = models.DateTimeField()

    def __str__(self):
        return f'{self.title} ({self.deadline:%d %b %H:%M})'

    def __repr__(self):
        return f'{self.title} ({self.deadline:%d %b %H:%M})'


class InspirationImage(AsyncModel):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=IMAGES_URL)

    def __str__(self):
        return f'{self.image} ({self.challenge.title})'

    def __repr__(self):
        return f'{self.image} ({self.challenge.title})'


class Submission(AsyncModel):
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    message_id = models.BigIntegerField(null=True)
    description = models.CharField(max_length=512, null=True)
    file_url = models.URLField()
    media_type = models.CharField(max_length=128)
    submitted_time = models.DateTimeField(auto_now=True)

    def get_html(self):
        if self.media_type.startswith('image'):
            return format_html(
                '<img src="{image_url}" width="150" height="150" style="object-fit: cover"/>',
                image_url=self.file_url
            )
        elif self.media_type.startswith('video'):
            return format_html(
                '''<video width="150" height="150" controls>
                  <source src="{video_url}" type="{media_type}">
                  </video>''',
                video_url=self.file_url,
                media_type=self.media_type
            )
        elif self.media_type.startswith('audio'):
            return format_html(
                '''<audio controls>
                  <source src="{audio_url}" type="{media_type}">
                  </audio>''',
                audio_url=self.file_url,
                media_type=self.media_type
            )
        else:
            return format_html(
                '<a href="{url}">{file_name}</a>',
                url=self.file_url,
                file_name=self.file_url.split('/')[-1]
            )

    def votes_count(self):
        return self.vote_set.count()

    def __str__(self):
        return f'Submission by {self.author} for {self.challenge.title}'

    def __repr__(self):
        return f'Submission by {self.author} for {self.challenge.title}'


class Vote(AsyncModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'submission')
