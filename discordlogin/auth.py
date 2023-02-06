from django.contrib.auth.backends import BaseBackend
from .models import DiscordUser
from django.http import HttpRequest


class DiscordAuthenticationBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, user: dict) -> DiscordUser:
        find_user = DiscordUser.objects.filter(discord_id=user["id"]).first()
        if not find_user:
            new_user = DiscordUser.objects.create_new_discord_user(user)
            return new_user
        return find_user

    def get_user(self, user_id):
        try:
            return DiscordUser.objects.get(pk=user_id)
        except DiscordUser.DoesNotExist:
            return None

    def get_username(self, user_id):
        try:
            return DiscordUser.objects.get(pk=user_id)
        except DiscordUser.DoesNotExist:
            return None
