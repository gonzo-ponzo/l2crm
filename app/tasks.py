from .models import Boss, Event
from discordlogin.models import CharacterServer
from l2crm.celery import app
from django.utils import timezone
from datetime import timedelta

@app.task
def update_event_respawn(boss: int, server: int):
    boss = Boss.objects.get(id=boss)
    last_event = Event.objects.filter(boss=boss).order_by("-respawn").first()
    if last_event.respawn < timezone.now() - timedelta(minutes=15):
        instance = Event(
            boss = boss,
            clan = "system",
            creator = "system",
            server = CharacterServer.objects.get(id=server),
            awakened = False,
            killed_at = timezone.now() - timedelta(minutes=14),
            closed_at = timezone.now() - timedelta(minutes=14),
            respawn = timezone.now() - timedelta(minutes=14) + timedelta(minutes=boss.respawn_time),
            was_respawned = True,
            was_reseted = False,
        )
        instance.save()
    return True