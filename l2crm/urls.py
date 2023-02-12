from django.contrib import admin
from django.urls import path, include
from discordlogin.views import (
    home_page,
    welcome_page,
    LogoutView,
    profile_page,
    UserView,
    RatingView,
    moderators,
)
from app.views import (
    EventListView,
    EventView,
    new_event_page,
    events_page,
    UpdateEvent,
    update_event_page,
    RespawnListView,
    MarketView,
    OfferView,
)
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", welcome_page, name="welcome-page"),
    path("discord-login/", include("discordlogin.urls"), name="discord-login"),
    path("logout", LogoutView.as_view(), name="logout-page"),
    path("home", home_page, name="home-page"),
    path("profile", profile_page, name="profile-page"),
    path("events", events_page, name="events-page"),
    path("moderators", moderators, name="moderator-page"),
    path("ratings", RatingView.as_view(), name="rating-page"),
    path(
        "events/all",
        login_required(EventListView.as_view(), login_url="/"),
        name="all-events-page",
    ),
    path(
        "events/respawns",
        login_required(RespawnListView.as_view(), login_url="/"),
        name="all-respawns-page",
    ),
    path(
        "events/<int:pk>/",
        login_required(EventView.as_view(), login_url="/"),
        name="event-page",
    ),
    path(
        "offers/<int:pk>/",
        login_required(OfferView.as_view(), login_url="/"),
        name="offer-page",
    ),
    path(
        "users/<int:pk>/",
        login_required(UserView.as_view(), login_url="/"),
        name="user-page",
    ),
    path(
        "market",
        login_required(MarketView.as_view(), login_url="/"),
        name="market-page",
    ),
    path("events/create", new_event_page, name="new-event-page"),
    path(
        "events/update/<int:pk>",
        login_required(UpdateEvent.as_view(), login_url="/"),
        name="update-event-page",
    ),
    path("ajax/load-drop/", update_event_page, name="ajax_load_drop"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
