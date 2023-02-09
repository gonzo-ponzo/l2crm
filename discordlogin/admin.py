from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    DiscordUser,
    Moderator,
    CharacterItem,
    CharacterSkills,
    CharacterClass,
    CharacterServer,
)


class CharacterItemsInLine(admin.TabularInline):
    model = CharacterItem
    fk_name = "user"
    extra = 1


class CharacterSkillsInLine(admin.TabularInline):
    model = CharacterSkills
    fk_name = "user"
    extra = 1


@admin.register(CharacterServer)
class CharacterServerAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


@admin.register(CharacterClass)
class CharacterClassAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


@admin.register(DiscordUser)
class UserAdmin(UserAdmin):
    list_display = [
        "id",
        "username",
        "nickname",
        "last_login",
        "character_clan",
        "character_party",
        "character_server",
        "score",
    ]
    search_fields = ("nickname", "character_clan")
    filter_horizontal = []
    fieldsets = (
        ("Discord", {"fields": ("nickname",)}),
        (
            "Ingame",
            {
                "fields": (
                    "character_server",
                    "character_clan",
                    "character_party",
                    "character_points",
                    "character_class",
                    "character_level",
                    "score",
                    "character_item_collections",
                    "character_card_collections",
                    "character_agation_collections",
                    "character_seal_collections",
                    "character_soul_collections",
                    "character_awaken_collections",
                )
            },
        ),
        (
            "Admin",
            {"fields": ("is_superuser", "is_admin", "is_moderator", "is_active")},
        ),
    )
    inlines = (
        CharacterItemsInLine,
        CharacterSkillsInLine,
    )


@admin.register(Moderator)
class ModeratorAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "moderator",
        "created_at",
    ]
    search_fields = ("id", "player", "moderator")
    fields = ("player", "moderator", "points", "text")
