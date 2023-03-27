from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView

from bot.models import User, Challenge


class UserProfileView(TemplateView):
    template_name = "profile.html"

    def get_context_data(self, user_id, **kwargs):
        user = get_object_or_404(User, discord_id=user_id)
        return {
            'user': user,
            'lives': user.get_lives_string()
        }


class ChallengeView(TemplateView):
    template_name = "challenge.html"

    def get_context_data(self, challenge_id, **kwargs):
        challenge = get_object_or_404(Challenge, pk=challenge_id)
        if challenge.start > timezone.now():
            return {
                'error': True
            }
        return {
            'challenge': challenge
        }
