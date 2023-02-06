from django.contrib.auth import models


class DiscordUserOAuth2Manager(models.UserManager):
    def create_new_discord_user(self, user):
        username = "%s#%s" % (user["username"], user["discriminator"])
        new_user = self.create(
            discord_id=user["id"],
            username=username,
            is_active=user["admin"],
            is_superuser=user["admin"],
            is_admin=user["admin"],
        )
        return new_user
