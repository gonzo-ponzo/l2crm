from .models import Boss, Event
from discordlogin.models import CharacterServer
from l2crm.celery import app
from django.utils import timezone
from datetime import timedelta, datetime


@app.task
def update_event_respawn(boss: int, server: int):
    now = timezone.now()
    boss = Boss.objects.get(id=boss)
    server = CharacterServer.objects.get(id=server)
    last_event = (
        Event.objects.filter(boss=boss, server=server).order_by("-respawn").first()
    )
    respawn = now - timedelta(minutes=5) + timedelta(minutes=boss.respawn_time)

    if last_event.respawn < now:
        instance = Event(
            boss=boss,
            clan="system",
            creator="system",
            server=server,
            awakened=False,
            killed_at=now - timedelta(minutes=5),
            respawn=respawn,
            was_closed=True,
            was_respawned=True,
            was_reseted=False,
        )
        instance.save()

        time_before = respawn - now
        seconds_before = int(time_before.total_seconds())
        update_event_respawn.apply_async(
            (boss.id, server.id), countdown=60 * 5 + seconds_before
        )
        return "%s True" % boss.name
    return False