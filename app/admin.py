from django.contrib import admin
from .models import (
    Boss,
    Item,
    SkillCard,
    Event,
    EventDrop,
    EventPlayers,
    BossLoot,
    OfferPlayers,
    Offer,
)


class BossLootInLine(admin.TabularInline):
    model = BossLoot
    fk_name = "boss"
    extra = 1


@admin.register(Boss)
class BossAdmin(admin.ModelAdmin):
    list_display = ("name", "respawn_time", "get_killed_at", "will_respawn_at")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("get_killed_at", "will_respawn_at")
    fields = (
        "name",
        "respawn_time",
        "respawn_chance",
        "respawn_delay",
        "points",
        "rarity",
        "get_killed_at",
        "will_respawn_at",
    )
    inlines = (BossLootInLine,)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "rarity", "type", "score", "price")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("rarity", "type")
    fields = ("name", "image", "rarity", "type", "score", "price")


@admin.register(SkillCard)
class SkillCardAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "rarity",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    fields = (
        "name",
        "rarity",
    )


class EventLootInLine(admin.TabularInline):
    model = EventDrop
    fk_name = "event"
    extra = 1


class EventPlayersInLine(admin.TabularInline):
    model = EventPlayers
    fk_name = "event"
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "boss",
        "server",
        "killed_at",
        "closed_at",
    )
    search_fields = ("boss",)
    fields = (
        "boss",
        "server",
        "awakened",
        "clan",
        "creator",
        "killed_at",
        "closed_at",
        "was_respawned",
    )
    inlines = (EventLootInLine, EventPlayersInLine)


class OfferPlayersInLine(admin.TabularInline):
    model = OfferPlayers
    fk_name = "offer"
    extra = 1


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "server",
        "active",
    )
    search_fields = ("item",)
    fields = ("item", "server", "active")
    inlines = (OfferPlayersInLine,)
