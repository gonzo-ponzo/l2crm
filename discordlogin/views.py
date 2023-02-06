from environs import Env
import requests
from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from constance import config
from app.models import Event
from .models import Moderator, DiscordUser
from django.views.generic import DetailView, ListView
from typing import Any, Dict


env = Env()
env.read_env()
auth_url_discord = env.str("AUTH_URL_DISCORD")
client_id = env.str("CLIENT_ID")
client_secret = env.str("CLIENT_SECRET")
guild_id = env.str("GUILD_ID")
API_ENDPOINT = "https://discord.com/api/v10"
redirect_uri = "https://l2crm.ru/discord-login/redirect"


def discord_login(request: HttpRequest) -> JsonResponse:
    return redirect(auth_url_discord)


def discord_login_redirect(request: HttpRequest):
    code = request.GET.get("code")
    user, roles, access_role, admin_role, member_ids = exchange_code(code)
    if user["id"] in member_ids:
        redirect("/")
    user["admin"] = admin_role in roles
    if access_role in roles:
        discord_user = authenticate(request, user=user)
        login(request, discord_user)
        return redirect("/home")
    else:
        return redirect("/")


def exchange_code(code: str) -> dict:
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "scope": "identify  guild guilds.members.read",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        "%s/oauth2/token" % API_ENDPOINT, data=data, headers=headers
    )
    credentials = response.json()
    access_token = credentials["access_token"]

    response = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": "Bearer %s" % access_token},
    )
    user = response.json()

    response = requests.get(
        "https://discord.com/api/guilds/1061352170437480508/members/%s" % user["id"],
        headers={"Authorization": "Bot %s" % env.str("BOT_TOKEN")},
    )
    user_roles = response.json()["roles"]

    response = requests.get(
        "https://discord.com/api/guilds/1061352170437480508/members?limit=1000",
        headers={"Authorization": "Bot %s" % env.str("BOT_TOKEN")},
    )
    members = response.json()
    member_ids = [member["user"]["id"] for member in members]

    response = requests.get(
        "https://discord.com/api/guilds/1061352170437480508/roles",
        headers={"Authorization": "Bot %s" % env.str("BOT_TOKEN")},
    )
    guild_roles = response.json()
    for role in guild_roles:
        if role["name"] == "Web access":
            access_role = role["id"]
        elif role["name"] == "Web admin":
            admin_role = role["id"]

    return user, user_roles, access_role, admin_role, member_ids


@login_required(login_url="/")
@csrf_protect
def home_page(request: HttpRequest):
    user = request.user
    if not user.character_server:
        return redirect("/profile")

    return render(
        request,
        "home.html",
        context={
            "total_item_collections": config.ITEM_COLLECTIONS,
            "item_collections_progress": round(
                (user.character_item_collections * 100 / config.ITEM_COLLECTIONS), 2
            ),
            "total_card_collections": config.CARD_COLLECTIONS,
            "card_collections_progress": round(
                (user.character_card_collections * 100 / config.CARD_COLLECTIONS), 2
            ),
            "total_agation_collections": config.AGATION_COLLECTIONS,
            "agation_collections_progress": round(
                (user.character_agation_collections * 100 / config.AGATION_COLLECTIONS),
                2,
            ),
            "total_seal_collections": config.SEAL_COLLECTIONS,
            "seal_collections_progress": round(
                (user.character_seal_collections * 100 / config.SEAL_COLLECTIONS),
                2,
            ),
            "total_soul_collections": config.SOUL_COLLECTIONS,
            "soul_collections_progress": round(
                (user.character_soul_collections * 100 / config.SOUL_COLLECTIONS),
                2,
            ),
            "total_awaken_collections": config.AWAKEN_COLLECTIONS,
            "awaken_collections_progress": round(
                (user.character_awaken_collections * 100 / config.AWAKEN_COLLECTIONS),
                2,
            ),
            "event_list": Event.objects.filter(
                players=user.id, server=user.character_server
            ).all(),
            "moderator_list": Moderator.objects.filter(player=user)
            .all()
            .order_by("-created_at")[:3],
        },
    )


class LogoutView(LogoutView):
    next_page = reverse_lazy("welcome-page")


@csrf_protect
def welcome_page(request: HttpRequest):
    return render(request, "non-autorized.html")


@login_required(login_url="/")
@csrf_protect
def profile_page(request: HttpRequest):
    from .models import CharacterClass, CharacterServer
    from app.models import Item, SkillCard

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
    items = Item.objects.all()
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

    user_items = user.character_items.values_list("id", flat=True).all()
    user_skills = user.character_skills.values_list("id", flat=True).all()

    if request.method == "POST":
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

        return redirect("/home")
    return render(
        request,
        "profile.html",
        context={
            "servers": CharacterServer.objects.all(),
            "game_classes": CharacterClass.objects.all(),
            "skills": SkillCard.objects.exclude(id__in=user_skills)
            .all()
            .order_by("name"),
            "character_skills": request.user.character_skills,
            "items": Item.objects.exclude(id__in=user_items).all().order_by("name"),
            "weapons_list": items.filter(type="Оружие").all(),
            "chests_list": items.filter(type="Верх. доспех").all(),
            "legs_list": items.filter(type="Нижн. доспех").all(),
            "gloves_list": items.filter(type="Перчатки").all(),
            "boots_list": items.filter(type="Сапоги").all(),
            "helmets_list": items.filter(type="Шлем").all(),
            "cloacks_list": items.filter(type="Плащ").all(),
            "shirts_list": items.filter(type="Рубашка").all(),
            "sigils_list": items.filter(type="Символ").all(),
            "neclaces_list": items.filter(type="Ожерелье").all(),
            "earrings_list": items.filter(type="Серьга").all(),
            "rings_list": items.filter(type="Кольцо").all(),
            "belts_list": items.filter(type="Пояс").all(),
            "bracers_list": items.filter(type="Браслет").all(),
            "inventory": inventory,
        },
    )


class RatingView(ListView):
    model = DiscordUser
    template_name = "rating.html"
    paginate_by = 10
    context_object_name = "users_list"

    def get_context_data(self, **kwargs):
        context = super(RatingView, self).get_context_data(**kwargs)
        context["server"] = self.request.user.character_server
        return context


class UserView(DetailView):
    model = DiscordUser
    template_name = "user.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super(UserView, self).get_context_data(**kwargs)
        user = DiscordUser.objects.get(id=self.kwargs["pk"])
        context["total_item_collections"] = config.ITEM_COLLECTIONS
        context["item_collections_progress"] = round(
            (user.character_item_collections * 100 / config.ITEM_COLLECTIONS), 2
        )
        context["total_card_collections"] = config.CARD_COLLECTIONS
        context["card_collections_progress"] = round(
            (user.character_card_collections * 100 / config.CARD_COLLECTIONS), 2
        )
        context["total_agation_collections"] = config.AGATION_COLLECTIONS
        context["agation_collections_progress"] = (
            round(
                (user.character_agation_collections * 100 / config.AGATION_COLLECTIONS),
                2,
            ),
        )
        context["total_seal_collections"] = config.SEAL_COLLECTIONS
        context["seal_collections_progress"] = round(
            (user.character_seal_collections * 100 / config.SEAL_COLLECTIONS),
            2,
        )
        context["total_soul_collections"] = config.SOUL_COLLECTIONS
        context["soul_collections_progress"] = round(
            (user.character_soul_collections * 100 / config.SOUL_COLLECTIONS),
            2,
        )
        context["total_awaken_collections"] = config.AWAKEN_COLLECTIONS
        context["awaken_collections_progress"] = round(
            (user.character_awaken_collections * 100 / config.AWAKEN_COLLECTIONS),
            2,
        )
        context["event_list"] = Event.objects.filter(
            players=user, server=user.character_server
        ).all()
        context["moderator_list"] = (
            Moderator.objects.filter(player=user).all().order_by("-created_at")[:3]
        )
        return context


@login_required(login_url="/")
@csrf_protect
def moderators(request: HttpRequest):
    user = request.user
    if not user.character_server:
        return redirect("/profile")

    if request.method == "POST":
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
        return redirect("/home")

    return render(
        request, "moderators.html", context={"players": DiscordUser.objects.all()}
    )


@login_required(login_url="/")
@csrf_protect
def reset_all_bosses(request: HttpRequest):
    import datetime
    from app.models import Boss
    from .models import CharacterServer

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

    return redirect("/home")
