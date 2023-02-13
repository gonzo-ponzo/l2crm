from .models import Boss, Event
from discordlogin.models import CharacterServer
from l2crm.celery import app
from django.utils import timezone
from datetime import timedelta


@app.task
def update_event_respawn(boss: int, server: int) -> bool:
    now = timezone.now()
    boss = Boss.objects.get(id=boss)
    server = CharacterServer.objects.get(id=server)
    last_event = (
        Event.objects.filter(boss=boss, server=server).order_by("-respawn").first()
    )
    respawn = now - timedelta(minutes=15) + timedelta(minutes=boss.respawn_time)

    if last_event.respawn < now:
        instance = Event(
            boss=boss,
            clan="system",
            creator="system",
            server=server,
            awakened=False,
            killed_at=now - timedelta(minutes=15),
            respawn=respawn,
            was_closed=True,
            was_respawned=True,
            was_reseted=False,
        )
        instance.save()

        time_before = respawn - now
        seconds_before = int(time_before.total_seconds())
        update_event_respawn.apply_async(
            (boss.id, server.id), countdown=60 * 15 + seconds_before
        )
        return True
    return False


@app.task
def close_event(event: int):
    event = Event.objects.get(id=event)
    event.was_closed = True
    event.save()
