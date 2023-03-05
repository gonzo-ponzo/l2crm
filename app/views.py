import datetime
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView, UpdateView
from django.utils import timezone
from .models import Event, Item, Boss, Offer
from .services import (
    participation_in_event,
    create_new_event,
    get_boss_list_to_display,
    give_item,
)


class EventListView(ListView):
    model = Event
    template_name = "events_all.html"
    paginate_by = 8

    def get_queryset(self):
        queryset = Event.objects.filter(
            server=self.request.user.character_server,
            was_respawned=False,
            was_reseted=False,
        ).all()[:80]
        return queryset


class RespawnListView(ListView):
    model = Event
    template_name = "respawns.html"
    paginate_by = 8

    def get_queryset(self):
        queryset = (
            Event.objects.filter(
                respawn__gt=datetime.datetime.now(),
                server=self.request.user.character_server,
            )
            .exclude(respawn=None)
            .order_by("respawn")
            .all()[:80]
        )
        return queryset


class EventView(DetailView):
    model = Event
    template_name = "event.html"

    def get_context_data(self, **kwargs):
        from django.utils import timezone

        context = super(EventView, self).get_context_data(**kwargs)
        invite = not self.object.was_closed
        context["invite"] = invite
        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        participation_in_event(request, self.get_object())
        return redirect(f"/events/{self.get_object().id}")


@login_required(login_url="/")
@csrf_protect
def new_event_page(request: HttpRequest):
    user = request.user
    if not user.character_server:
        return redirect("/profile")

    if request.method == "POST":
        create_new_event(request)
        return redirect("/events")

    boss_list = get_boss_list_to_display(user.character_server)

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
            ).all()[0:15],
            "respawn_list": Event.objects.filter(
                respawn__gt=timezone.now(),
                server=request.user.character_server,
            )
            .exclude(respawn=None)
            .order_by("respawn")
            .all()[0:15],
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

        self.object = self.get_object()
        if self.request.POST.get("give") == "give":
            give_item(self.request, self.object)
            return redirect("/home")
        else:
            if request.user not in self.object.players.all():
                self.object.players.add(request.user)
        return redirect(f"/offers/{self.object.id}")
