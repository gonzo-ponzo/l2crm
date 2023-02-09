from .models import CharacterClass, CharacterServer, DiscordUser, Moderator
from app.models import Item, SkillCard, Event, Boss
from django.http import HttpRequest
from constance import config
import datetime

field_names = {
    "weapon": "Оружие",
    "chest": "Верх. доспех",
    "legs": "Нижн. доспех",
    "helmet": "Шлем",
    "gloves": "Перчатки",
    "boots": "Сапоги",
    "cloack": "Плащ",
    "shirt": "Рубашка",
    "sigil": "Символ",
    "neclace": "Ожерелье",
    "ring1": "Кольцо",
    "ring2": "Кольцо",
    "earring1": "Серьга",
    "earring2": "Серьга",
    "belt": "Пояс",
    "bracer": "Браслет",
}


def get_user_inventory(request: HttpRequest) -> dict:
    user = request.user
    inventory = {}

    for html_type, item_type in field_names.items():
        if html_type in ("ring1", "earring1"):
            try:
                inventory[html_type] = user.character_items.filter(
                    type=item_type
                ).all()[0]
            except:
                inventory[html_type] = None
        elif html_type in ("ring2", "earring2"):
            try:
                inventory[html_type] = user.character_items.filter(
                    type=item_type
                ).all()[1]
            except:
                inventory[html_type] = None
        else:
            inventory[html_type] = user.character_items.filter(type=item_type).first()
    return inventory


def set_user_data(request: HttpRequest) -> None:
    user = request.user

    user.character_server = CharacterServer.objects.filter(
        id=request.POST.get("character_server")
    ).first()
    user.character_clan = request.POST.get("character_clan")
    user.nickname = request.POST.get("character_nickname")
    user.character_party = request.POST.get("character_party")
    user.character_class = CharacterClass.objects.filter(
        id=request.POST.get("character_game_class")
    ).first()
    user.character_level = request.POST.get("character_level")

    if (
        int(config.ITEM_COLLECTIONS)
        >= int(request.POST.get("character_item_collections"))
        > user.character_item_collections
    ):
        user.character_points += (
            int(request.POST.get("character_item_collections"))
            - user.character_item_collections
        ) * int(config.DKP_PER_COLLECTION)
        user.character_item_collections = int(
            request.POST.get("character_item_collections")
        )

    if (
        int(config.CARD_COLLECTIONS)
        >= int(request.POST.get("character_card_collections"))
        > user.character_card_collections
    ):
        user.character_points += (
            int(request.POST.get("character_card_collections"))
            - user.character_card_collections
        ) * int(config.DKP_PER_COLLECTION)
        user.character_card_collections = int(
            request.POST.get("character_card_collections")
        )

    if (
        int(config.AGATION_COLLECTIONS)
        >= int(request.POST.get("character_agation_collections"))
        > user.character_agation_collections
    ):
        user.character_points += (
            int(request.POST.get("character_agation_collections"))
            - user.character_agation_collections
        ) * int(config.DKP_PER_COLLECTION)
        user.character_agation_collections = int(
            request.POST.get("character_agation_collections")
        )

    if (
        int(config.SEAL_COLLECTIONS)
        >= int(request.POST.get("character_seal_collections"))
        > user.character_seal_collections
    ):
        user.character_points += (
            int(request.POST.get("character_seal_collections"))
            - user.character_seal_collections
        ) * int(config.DKP_PER_COLLECTION)
        user.character_seal_collections = int(
            request.POST.get("character_seal_collections")
        )

    if (
        int(config.SOUL_COLLECTIONS)
        >= int(request.POST.get("character_soul_collections"))
        > user.character_soul_collections
    ):
        user.character_points += (
            int(request.POST.get("character_soul_collections"))
            - user.character_soul_collections
        ) * int(config.DKP_PER_COLLECTION)
        user.character_soul_collections = int(
            request.POST.get("character_soul_collections")
        )

    if (
        int(config.AWAKEN_COLLECTIONS)
        >= int(request.POST.get("character_awaken_collections"))
        > user.character_awaken_collections
    ):
        user.character_points += (
            int(request.POST.get("character_awaken_collections"))
            - user.character_awaken_collections
        ) * int(config.DKP_PER_COLLECTION)
        user.character_awaken_collections = int(
            request.POST.get("character_awaken_collections")
        )

    skills = request.POST.getlist("character_skills")
    for skill in skills:
        user.character_skills.add(SkillCard.objects.get(id=skill))

    user.character_items.clear()
    user.score = 0
    for field in field_names:
        item_name = request.POST.get(field)
        item = Item.objects.filter(name=item_name).first()
        if item:
            user.score += item.score
            user.character_items.add(item)
    user.save()


def create_new_report(request: HttpRequest):
    player = DiscordUser.objects.get(id=request.POST.get("player"))
    points = request.POST.get("points")
    report = Moderator(
        player=player,
        moderator=request.user.nickname,
        points=points,
        text=request.POST.get("reason"),
    )
    report.save()
    player.character_points += int(points)
    player.save()


def restart_bosses() -> None:
    respawns = (
        Event.objects.filter(respawn__gt=datetime.datetime.now())
        .exclude(respawn=None)
        .all()
    )
    for respawn in respawns:
        respawn.respawn = datetime.datetime.now()
        respawn.closed_at = datetime.datetime.now() - datetime.timedelta(minutes=120)
        respawn.save()
    bosses = Boss.objects.filter(respawn_delay__gt=0).all()
    servers = CharacterServer.objects.all()
    for server in servers:
        for boss in bosses:
            instance = Event(
                boss=boss,
                awakened=False,
                was_respawned=False,
                was_reseted=True,
                clan="system",
                server=server,
                creator="system",
                killed_at=datetime.datetime.now(),
                closed_at=datetime.datetime.now(),
                respawn=datetime.datetime.now()
                + datetime.timedelta(minutes=boss.respawn_delay),
            )
            instance.save()
