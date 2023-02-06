from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from .models import Event, Item, Boss, Offer
from django.views.generic import ListView, DetailView, UpdateView
from django.views.decorators.csrf import csrf_protect
import datetime
from environs import Env
from discord import SyncWebhook, Embed


env = Env()
env.read_env()
discord_webhook = env.str("DISCORD_WEBHOOK")
webhook = SyncWebhook.from_url(discord_webhook)


class EventListView(ListView):
    model = Event
    template_name = "events_all.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Event.objects.filter(
            server=self.request.user.character_server,
            was_respawned=False,
            was_reseted=False,
        ).all()
        return queryset


class RespawnListView(ListView):
    model = Event
    template_name = "respawns.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Event.objects.filter(
                respawn__gt=datetime.datetime.now(),
                server=self.request.user.character_server,
            )
            .exclude(respawn=None)
            .order_by("respawn")
            .all()
        )
        return queryset


class EventView(DetailView):
    model = Event
    template_name = "event.html"

    def get_context_data(self, **kwargs):
        from django.utils import timezone

        context = super(EventView, self).get_context_data(**kwargs)
        now = timezone.now()
        invite = self.object.closed_at > now
        context["invite"] = invite
        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        self.object = self.get_object()
        points = self.object.boss.points

        if request.POST.get("event_player"):
            if request.user in self.object.players.all():
                self.object.players.remove(request.user)
                if self.object.awakened:
                    request.user.character_points -= points * 10
                else:
                    request.user.character_points -= points
                request.user.save()
        else:
            if request.user not in self.object.players.all():
                self.object.players.add(request.user)
                if self.object.awakened:
                    request.user.character_points += points * 10
                else:
                    request.user.character_points += points
                request.user.save()

        return redirect(f"/events/{self.object.id}")


@login_required(login_url="/")
@csrf_protect
def new_event_page(request: HttpRequest):
    import datetime
    from django.utils import timezone

    user = request.user
    if not user.character_server:
        return redirect("/profile")

    if request.method == "POST":
        date = datetime.datetime.strptime(
            request.POST.get("event_killed_at_date"), "%Y-%m-%d"
        ).date()
        time = datetime.datetime.strptime(
            request.POST.get("event_killed_at_time"), "%H:%M"
        ).time()
        killed_at = datetime.datetime.combine(date, time)
        if request.POST.get("event_awakened") == "True":
            flag = True
        else:
            flag = False
        boss = Boss.objects.get(id=request.POST.get("event_boss"))
        server = request.user.character_server
        if request.POST.get("event_was_respawned"):
            respawned = True
        else:
            respawned = False
        instance = Event(
            boss=boss,
            awakened=flag,
            was_respawned=respawned,
            clan=request.user.character_clan,
            server=server,
            creator=request.user.nickname,
            killed_at=killed_at,
            closed_at=killed_at + datetime.timedelta(hours=2),
            respawn=killed_at
            + datetime.timedelta(
                minutes=Boss.objects.get(id=request.POST.get("event_boss")).respawn_time
            ),
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
        # TODO webhook notification
        # embed = Embed(
        #     title=f"{boss.name} {server.name}",
        #     color=3064446,
        #     description="Драк лук, драк шлем, АС",
        #     url=f"https://localhost:8000/events/{instance.id}/",
        # )
        # webhook.send(username="L2 CRM", content="Создано новое событие", embed=embed)

        return redirect("/events")

    boss_list = []
    now = timezone.now()
    bosses = Boss.objects.all()
    for boss in bosses:
        event_boss = Event.objects.filter(boss=boss.id).order_by("-closed_at").first()
        if event_boss:
            if event_boss.closed_at < now and event_boss.respawn < now:
                boss_list.append(boss)
        elif event_boss == None:
            boss_list.append(boss)
    return render(
        request,
        "event-create.html",
        context={
            "bosses": boss_list,
            "items": Item.objects.all(),
        },
    )


class UpdateEvent(UpdateView):
    def get(self, request: HttpRequest, boss_id: int, *args, **kwargs):
        return render(
            request,
            "event-create.html",
            context={
                "bosses": Boss.objects.get(id=boss_id),
                "items": Boss.objects.filter(id=boss_id).first().values_list("loot"),
            },
        )


@login_required(login_url="/")
@csrf_protect
def update_event_page(request: HttpRequest):
    boss_id = request.GET.get("boss")
    boss = Boss.objects.get(id=boss_id)
    items = Item.objects.filter(boss=boss).all()
    return render(request, "drop_list.html", {"items": items})


@login_required(login_url="/")
@csrf_protect
def events_page(request: HttpRequest):
    return render(
        request,
        "events.html",
        context={
            "event_list": Event.objects.filter(
                server=request.user.character_server,
                was_respawned=False,
                was_reseted=False,
            ).all()[0:9],
            "respawn_list": Event.objects.filter(
                respawn__gt=datetime.datetime.now(),
                server=request.user.character_server,
            )
            .exclude(respawn=None)
            .order_by("respawn")
            .all()[0:9],
        },
    )


class MarketView(ListView):
    model = Offer
    template_name = "market.html"
    paginate_by = 10
    context_object_name = "offers"

    def get_context_data(self, **kwargs):
        context = super(MarketView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        queryset = (
            Offer.objects.filter(server=self.request.user.character_server)
            .exclude(active=False)
            .all()
        )
        return queryset


class OfferView(DetailView):
    model = Offer
    template_name = "offer.html"

    def post(self, request: HttpRequest, *args, **kwargs):
        from discordlogin.models import DiscordUser, Moderator

        self.object = self.get_object()
        if self.request.POST.get("give") == "give":
            user_id = self.request.POST.get("offer_player")
            user = DiscordUser.objects.get(id=user_id)
            user.character_points -= self.object.item.price
            user.save()
            self.object.active = False
            self.object.save()
            moderator = Moderator(
                player=user,
                moderator=request.user.nickname,
                points=self.object.item.price * (-1),
                text=f"Покупка {self.object.item.name}",
            )
            moderator.save()
            return redirect("/home")
        else:
            if request.user not in self.object.players.all():
                self.object.players.add(request.user)
        return redirect(f"/offers/{self.object.id}")
