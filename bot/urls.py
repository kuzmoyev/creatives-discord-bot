from django.urls import path

from bot.views import UserProfileView

urlpatterns = [
    path('profile/<int:user_id>', UserProfileView.as_view(), name='profile'),
]
