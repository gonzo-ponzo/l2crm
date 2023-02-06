from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator


RARITY = (
    ("blue", "blue"),
    ("red", "red"),
    ("purple", "purple"),
    ("gold", "gold"),
)

ITEM_TYPES = (
    ("Оружие", "Оружие"),
    ("Верх. доспех", "Верх. доспех"),
    ("Нижн. доспех", "Нижн. доспех"),
    ("Перчатки", "Перчатки"),
    ("Сапоги", "Сапоги"),
    ("Шлем", "Шлем"),
    ("Плащ", "Плащ"),
    ("Рубашка", "Рубашка"),
    ("Символ", "Символ"),
    ("Ожерелье", "Ожерелье"),
    ("Серьга", "Серьга"),
    ("Кольцо", "Кольцо"),
    ("Пояс", "Пояс"),
    ("Браслет", "Браслет"),
    ("Книга умений", "Книга умений"),
    ("Душа", "Душа"),
    ("Разное", "Разное"),
)


class Boss(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    respawn_time = models.IntegerField(verbose_name="Время респа")
    get_killed_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Время последнего убийства"
    )
    will_respawn_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Время следующего респа"
    )
    loot = models.ManyToManyField(
        "Item", through="BossLoot", verbose_name="Список дропа"
    )
    points = models.IntegerField(default=0, verbose_name="PTS награда")
    rarity = models.CharField(
        max_length=20, choices=RARITY, default="blue", verbose_name="Редкость"
    )
    respawn_chance = models.IntegerField(default=100, verbose_name="Шанс респа")
    respawn_delay = models.IntegerField(default=0, verbose_name="Отложенный респ")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Босс"
        verbose_name_plural = "Боссы"


class Item(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование")
    image = models.ImageField(
        upload_to="item/%Y/%m/%d", blank=True, verbose_name="Изображение"
    )
    rarity = models.CharField(
        max_length=20, choices=RARITY, default="blue", verbose_name="Редкость"
    )
    type = models.CharField(
        max_length=20, choices=ITEM_TYPES, default="Оружие", verbose_name="Тип"
    )
    score = models.PositiveIntegerField(default=0, verbose_name="Рейтинг")
    price = models.PositiveIntegerField(default=0, verbose_name="Цена DKP")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"


class BossLoot(models.Model):
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE, verbose_name="Босс")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Предмет")

    class Meta:
        verbose_name = "Лут"
        verbose_name_plural = "Лут"

    def __str__(self) -> str:
        return self.item.name


class SkillCard(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    rarity = models.CharField(
        max_length=20, choices=RARITY, default="BLUE", verbose_name="Редкость"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Скилл"
        verbose_name_plural = "Скиллы"


class Event(models.Model):
    from discordlogin.models import DiscordUser, CharacterServer

    boss = models.ForeignKey(
        Boss, default=None, null=True, on_delete=models.CASCADE, verbose_name="Босс"
    )
    clan = models.CharField(
        max_length=20, default=None, null=True, verbose_name="Название клана"
    )
    creator = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=("Автор события")
    )
    server = models.ForeignKey(
        CharacterServer,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Сервер",
    )
    awakened = models.BooleanField(default=False, verbose_name="Пробужденный")
    drop = models.ManyToManyField(
        "Item", through="EventDrop", verbose_name="Список дропа"
    )
    players = models.ManyToManyField(
        DiscordUser, through="EventPlayers", verbose_name="Список участников"
    )
    killed_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Время убийства"
    )
    closed_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Время закрытия"
    )
    respawn = models.DateTimeField(blank=True, null=True, verbose_name="Время респа")
    was_respawned = models.BooleanField(default=False, verbose_name="Не воскрешен")
    was_reseted = models.BooleanField(
        default=False, blank=True, null=True, verbose_name="Обнулен"
    )

    def __str__(self) -> str:
        return self.boss.name

    def get_absolute_url(self):
        return reverse("event-page", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ["-killed_at"]


class EventDrop(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Событие")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Предмет")

    def __str__(self) -> str:
        return self.item.name

    class Meta:
        verbose_name = "Дроп"
        verbose_name_plural = "Дроп"


class EventPlayers(models.Model):
    from discordlogin.models import DiscordUser

    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Событие")
    player = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, verbose_name="Профиль"
    )

    def __str__(self) -> str:
        return self.player.username

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"


class Offer(models.Model):
    from discordlogin.models import DiscordUser, CharacterServer

    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Предмет")
    active = models.BooleanField(default=True, verbose_name="Статус")
    players = models.ManyToManyField(
        DiscordUser, through="OfferPlayers", verbose_name="Список участников"
    )
    event = models.ForeignKey(
        Event, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Событие"
    )
    server = models.ForeignKey(
        CharacterServer,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Сервер",
    )

    def get_absolute_url(self):
        return reverse("offer-page", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "Лот"
        verbose_name_plural = "Лоты"


class OfferPlayers(models.Model):
    from discordlogin.models import DiscordUser

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, verbose_name="Лот")
    player = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, verbose_name="Профиль"
    )

    def __str__(self) -> str:
        return self.player.username

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
