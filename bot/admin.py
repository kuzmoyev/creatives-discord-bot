from urllib.parse import urljoin

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import Group

from bot.models import User, Challenge, InspirationImage, Submission, Vote
from creatives_discord_bot.settings import DISCORD_SUBMISSION_URL

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'discord_id',
        'display_name',
        'avatar_tag',
        'registered',
        'lives',
        'profile'
    )

    fields = (
        'discord_id',
        'display_name',
        'avatar_url',
        'avatar_tag',
        'lives',
    )
    readonly_fields = ['avatar_tag']

    def avatar_tag(self, user):
        return format_html('<img src="{image_url}" width="50" height="50"/>', image_url=user.avatar_url)

    def profile(self, user):
        return format_html('<a href="/profile/{user_id}">profile</a>', user_id=user.discord_id)

    avatar_tag.short_description = 'avatar'


class InspirationImageInline(admin.StackedInline):
    model = InspirationImage


@admin.register(InspirationImage)
class InspirationImageAdmin(admin.ModelAdmin):
    list_display = (
        'image_tag',
    )

    def image_tag(self, image: InspirationImage):
        return format_html('<img src="{image_url}" width="50" height="50"/>',
                           image_url=image.image.url)

    image_tag.short_description = 'image'


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'start',
        'deadline',
        'submissions'
    )

    inlines = (InspirationImageInline,)

    def submissions(self, challenge):
        base_url = reverse('admin:bot_submission_changelist')
        return format_html(
            '<a href="{base_url}?challenge_id__exact={challenge_id}">{count}</a>',
            base_url=base_url,
            challenge_id=challenge.id,
            count=challenge.submissions_count
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(submissions_count=Count("submission"))
        return queryset


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'file',
        'author',
        'challenge',
        'media_type',
        'message',
        'submitted_time',
        'votes_count'
    )

    list_filter = (
        'author',
        'challenge',
    )

    def file(self, submission):
        return submission.get_html()

    def message(self, submission):
        url = urljoin(DISCORD_SUBMISSION_URL, str(submission.message_id))
        return format_html(
            '<a href="{url}">{message_id}</a>',
            url=url,
            message_id=submission.message_id
        )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'submission'
    )

    list_filter = (
        'user',
        'submission'
    )
