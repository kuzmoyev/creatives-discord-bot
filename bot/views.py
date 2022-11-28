from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from bot.models import User


class UserProfileView(TemplateView):
    template_name = "profile.html"

    def get_context_data(self, user_id, **kwargs):
        user = get_object_or_404(User, discord_id=user_id)
        return {
            'user': user,
            'lives': '♥️' * user.lives + '♡' * (3 - user.lives)
        }
