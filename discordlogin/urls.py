from django.urls import path
from .views import discord_login, discord_login_redirect

urlpatterns = [
    path("", discord_login, name="discord-auth"),
    path("redirect/", discord_login_redirect, name="discord-auth-redirect"),
]
