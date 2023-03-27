from django.urls import path

from bot.views import UserProfileView, ChallengeView

urlpatterns = [
    path('profile/<int:user_id>', UserProfileView.as_view(), name='profile'),
    path('challenge/<int:challenge_id>', ChallengeView.as_view(), name='challenge'),
]
