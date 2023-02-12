from django.http import HttpRequest
from .models import Event, Boss, Item, Offer
from discordlogin.models import DiscordUser, Moderator, CharacterServer
import datetime
from environs import Env
from .tasks import update_event_respawn


env = Env()
env.read_env()


def participation_in_event(request: HttpRequest, event: Event) -> None:
    points = event.boss.points
    if request.POST.get("event_player"):
        if request.user in event.players.all():
            event.players.remove(request.user)
            if event.awakened:
                request.user.character_points -= points * 10
            else:
                request.user.character_points -= points
            request.user.save()
    else:
        if request.user not in event.players.all():
            event.players.add(request.user)
            if event.awakened:
                request.user.character_points += points * 10
            else:
                request.user.character_points += points
            request.user.save()


def create_new_event(request: HttpRequest) -> None:
    from discord import SyncWebhook, Embed

    discord_webhook = env.str("DISCORD_WEBHOOK")
    webhook = SyncWebhook.from_url(discord_webhook)

    date = datetime.datetime.strptime(
        request.POST.get("event_killed_at_date"), "%Y-%m-%d"
    ).date()
    time = datetime.datetime.strptime(
        request.POST.get("event_killed_at_time"), "%H:%M"
    ).time()
    killed_at = datetime.datetime.combine(date, time)
    respawn = killed_at + datetime.timedelta(
        minutes=Boss.objects.get(id=request.POST.get("event_boss")).respawn_time
    )
    flag = True if request.POST.get("event_awakened") == "True" else False
    boss = Boss.objects.get(id=request.POST.get("event_boss"))
    server = request.user.character_server
    respawned = True if request.POST.get("event_was_respawned") else False

    instance = Event(
        boss=boss,
        awakened=flag,
        was_respawned=respawned,
        clan=request.user.character_clan,
        server=server,
        creator=request.user.nickname,
        killed_at=killed_at,
        respawn=respawn,
    )
    instance.save()

    drop = request.POST.getlist("event_drop")
    for item in drop:
        instance.drop.add(Item.objects.get(id=item))
        offer = Offer(
            item=Item.objects.get(id=item),
            event=instance,
            server=request.user.character_server,
        )
        offer.save()
    instance.save()
    if instance.was_respawned:
        request.user.character_points += 50
    else:
        request.user.character_points += 20
    request.user.save()
    time_before = respawn - datetime.datetime.now()
    seconds_before = int(time_before.total_seconds())
    update_event_respawn.apply_async(
        (boss.id, server.id), countdown=60 * 5 + seconds_before
    )

    # TODO webhook notification
    # embed = Embed(
    #     title=f"{boss.name} {server.name}",
    #     color=3064446,
    #     description="Драк лук, драк шлем, АС",
    #     url=f"https://localhost:8000/events/{instance.id}/",
    # )
    # webhook.send(username="L2 CRM", content="Создано новое событие", embed=embed)


def get_boss_list_to_display(server: CharacterServer) -> list[Boss]:
    boss_list = []
    bosses = Boss.objects.all()
    for boss in bosses:
        opened_event = Event.objects.filter(
            boss=boss.id, respawn__gt=datetime.datetime.now(), server=server
        ).first()
        if not opened_event or opened_event == None:
            boss_list.append(boss)
    return boss_list


def give_item(request: HttpRequest, offer: Offer) -> None:
    user_id = request.POST.get("offer_player")
    user = DiscordUser.objects.get(id=user_id)
    user.character_points -= offer.item.price
    user.save()
    offer.active = False
    offer.save()
    moderator = Moderator(
        player=user,
        moderator=request.user.nickname,
        points=offer.item.price * (-1),
        text=f"Покупка {offer.item.name}",
    )
    moderator.save()
