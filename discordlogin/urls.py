from django.urls import path, re_path
from .views import discord_login, discord_login_redirect
from django.conf import settings
from django.views.static import serve 

urlpatterns = [
    path("", discord_login, name="discord-auth"),
    path("redirect/", discord_login_redirect, name="discord-auth-redirect"),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
]
