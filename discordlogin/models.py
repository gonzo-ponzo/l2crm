from django.db import models
from .managers import DiscordUserOAuth2Manager
from django.http import HttpRequest
from app.models import Item, SkillCard
from django.urls import reverse
from constance import config
from django.core.validators import MaxValueValidator


class CharacterServer(models.Model):
    name = models.CharField(max_length=20, verbose_name="Игровой сервер")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Сервер"
        verbose_name_plural = "Серверы"


class CharacterClass(models.Model):
    name = models.CharField(max_length=20, verbose_name="Игровой класс")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"


class DiscordUser(models.Model):
    objects = DiscordUserOAuth2Manager()
    USERNAME_FIELD = "nickname"

    discord_id = models.BigIntegerField(verbose_name="Индентификатор в дискорде")
    username = models.CharField(max_length=100, verbose_name="Юзернэйм")
    nickname = models.CharField(
        max_length=100, blank=True, null=True, unique=True, verbose_name="Никнейм"
    )
    score = models.PositiveIntegerField(default=0, verbose_name="Рейтинг")
    character_server = models.ForeignKey(
        CharacterServer,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Сервер",
    )
    character_clan = models.CharField(max_length=100, blank=True, verbose_name="Клан")
    character_party = models.CharField(max_length=100, blank=True, verbose_name="КП")
    character_points = models.IntegerField(default=0, verbose_name="Количество DKP")
    character_class = models.ForeignKey(
        CharacterClass,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Класс",
    )
    character_skills = models.ManyToManyField(
        SkillCard, blank=True, through="CharacterSkills", verbose_name="Скилы"
    )
    character_level = models.PositiveIntegerField(
        default=1, verbose_name="Уровень героя"
    )
    character_item_collections = models.PositiveIntegerField(
        validators=[MaxValueValidator(config.ITEM_COLLECTIONS)],
        default=0,
        verbose_name="Количество коллекций предметов",
    )
    character_card_collections = models.PositiveIntegerField(
        validators=[MaxValueValidator(config.CARD_COLLECTIONS)],
        default=0,
        verbose_name="Количество коллекций героев",
    )
    character_agation_collections = models.PositiveIntegerField(
        validators=[MaxValueValidator(config.AGATION_COLLECTIONS)],
        default=0,
        verbose_name="Количество коллекций агатионов",
    )
    character_seal_collections = models.PositiveIntegerField(
        validators=[MaxValueValidator(config.SEAL_COLLECTIONS)],
        default=0,
        verbose_name="Количество коллекций печатей",
    )
    character_soul_collections = models.PositiveIntegerField(
        validators=[MaxValueValidator(config.SOUL_COLLECTIONS)],
        default=0,
        verbose_name="Количество коллекций души",
    )
    character_awaken_collections = models.PositiveIntegerField(
        validators=[MaxValueValidator(config.AWAKEN_COLLECTIONS)],
        default=0,
        verbose_name="Количество пробуждений",
    )
    character_items = models.ManyToManyField(
        Item, blank=True, through="CharacterItem", verbose_name="Предметы"
    )
    last_login = models.DateTimeField(
        blank=True, null=True, verbose_name="Последний визит"
    )

    is_admin = models.BooleanField(default=False, verbose_name="Админ")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    is_staff = models.BooleanField(default=True, verbose_name="Служебный")
    is_superuser = models.BooleanField(default=True, verbose_name="Суперюзер")
    is_moderator = models.BooleanField(default=False, verbose_name="Модератор")

    def __str__(self):
        return self.nickname

    @property
    def is_staff(self):
        return self.is_admin

    def is_authenticated(self, request: HttpRequest) -> bool:
        return True

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_username(self):
        return self.username

    def get_absolute_url(self):
        return reverse("user-page", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class CharacterItem(models.Model):
    user = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, verbose_name="Персонаж"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Предмет")

    def __str__(self) -> str:
        return self.item.name

    class Meta:
        verbose_name = "Предмет героя"
        verbose_name_plural = "Предметы героя"


class CharacterSkills(models.Model):
    user = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, verbose_name="Персонаж"
    )
    skill = models.ForeignKey(SkillCard, on_delete=models.CASCADE, verbose_name="Скил")

    def __str__(self) -> str:
        return self.skill.name

    class Meta:
        verbose_name = "Скилл героя"
        verbose_name_plural = "Скиллы героя"


class Moderator(models.Model):
    player = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, verbose_name="Игрок"
    )
    moderator = models.CharField(max_length=50, verbose_name="Модератор")
    points = models.IntegerField(verbose_name="Кол-во DKP")
    text = models.TextField(max_length=500, verbose_name="Решение модератора")
    created_at = models.DateTimeField(auto_now=True, verbose_name="Время создания")

    class Meta:
        verbose_name = "Модерирование"
        verbose_name_plural = "Модерирования"
