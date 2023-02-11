from environs import Env
from pathlib import Path
import os


env = Env()
env.read_env()

ROOT_PATH = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


POSTGRES_DB = env.str("POSTGRES_DB")
POSTGRES_USER = env.str("POSTGRES_USER")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
POSTGRES_HOST = env.str("POSTGRES_HOST")
POSTGRES_PORT = env.str("POSTGRES_PORT")

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = env.str("DEBUG")

ALLOWED_HOSTS = env.str("ALLOWED_HOSTS").split(" ")

AUTHENTICATION_BACKENDS = ["discordlogin.auth.DiscordAuthenticationBackend"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "constance",
    "app",
    "discordlogin.apps.DiscordloginConfig",
    "django_celery_beat",
    "django_celery_results",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "l2crm.urls"

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["static", "templates", BASE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis_db:6379",
    }
}

# Django-constance settings
CONSTANCE_BACKEND = "constance.backends.redisd.CachingRedisBackend"
CONSTANCE_REDIS_CONNECTION = "redis://redis_db:6379"
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True
CONSTANCE_REDIS_CACHE_TIMEOUT = 0

CONSTANCE_CONFIG = {
    "ITEM_COLLECTIONS": (100, "Всего коллекций предметов"),
    "CARD_COLLECTIONS": (100, "Всего коллекций героев"),
    "AGATION_COLLECTIONS": (100, "Всего коллекций агатионов"),
    "SEAL_COLLECTIONS": (100, "Всего коллекций печатей"),
    "SOUL_COLLECTIONS": (100, "Всего коллекций души"),
    "AWAKEN_COLLECTIONS": (100, "Всего пробуждений"),
    "DKP_PER_COLLECTION": (0, "ДКП за закрытие коллекции"),
}

SESSION_COOKIE_AGE = 60 * 60 * 24

WSGI_APPLICATION = "l2crm.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "ru"
DATETIME_FORMAT = "H:i d.m"
USE_L10N = False
TIME_ZONE = "Europe/Moscow"
USE_TZ = True
USE_I18N = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LOGIN_URL = "/login/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = ["https://l2crm.ru", "https://www.l2crm.ru"]

CELERY_BROKER_URL = "redis://redis_db:6379"
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "default"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
