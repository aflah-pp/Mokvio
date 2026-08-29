from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env(
    DEBUG=(bool, False),
)


ENVIRONMENT = env(
    "DJANGO_ENV",
    default="development",
).lower()


if ENVIRONMENT not in {"development", "production"}:
    raise ValueError("DJANGO_ENV must be either 'development' or 'production'.")


ENV_FILE = (
    BASE_DIR / ".env.production"
    if ENVIRONMENT == "production"
    else BASE_DIR / ".env.development"
)


if ENV_FILE.exists():
    environ.Env.read_env(ENV_FILE)


SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool(
    "DEBUG",
    default=ENVIRONMENT == "development",
)


ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"],
)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "users",
    "projects",
    "resources",
    "runtime",
    "dashboard",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"

AUTH_USER_MODEL = "users.User"

WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


if ENVIRONMENT == "production":
    DATABASES = {
        "default": env.db("DATABASE_URL"),
    }
else:
    DATABASES = {
        "default": env.db(
            "DATABASE_URL",
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        ),
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator"),
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = env(
    "TIME_ZONE",
    default="Asia/Kolkata",
)

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": ("whitenoise.storage.CompressedManifestStaticFilesStorage"),
    },
}


MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ),
    "DEFAULT_PAGINATION_CLASS": ("rest_framework.pagination.PageNumberPagination",),
    "PAGE_SIZE": env.int(
        "API_PAGE_SIZE",
        default=20,
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": env(
            "DRF_ANON_RATE",
            default="30/min",
        ),
        "user": env(
            "DRF_USER_RATE",
            default="120/min",
        ),
    },
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int(
            "JWT_ACCESS_TOKEN_MINUTES",
            default=15,
        ),
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int(
            "JWT_REFRESH_TOKEN_DAYS",
            default=7,
        ),
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}


CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:5173",
    ],
)


CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost:5173",
    ],
)


CORS_ALLOW_CREDENTIALS = True


JWT_REFRESH_COOKIE_NAME = env(
    "JWT_REFRESH_COOKIE_NAME",
    default="refresh_token",
)


JWT_REFRESH_COOKIE_MAX_AGE = env.int(
    "JWT_REFRESH_COOKIE_MAX_AGE",
    default=604800,
)


JWT_REFRESH_COOKIE_SECURE = env.bool(
    "JWT_REFRESH_COOKIE_SECURE",
    default=False,
)


JWT_REFRESH_COOKIE_SAMESITE = env(
    "JWT_REFRESH_COOKIE_SAMESITE",
    default="Lax",
)


JWT_REFRESH_COOKIE_DOMAIN = env(
    "JWT_REFRESH_COOKIE_DOMAIN",
    default=None,
)


JWT_REFRESH_COOKIE_PATH = env(
    "JWT_REFRESH_COOKIE_PATH",
    default="/",
)


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = "noreply@mokvio.local"


SECURE_SSL_REDIRECT = env.bool(
    "SECURE_SSL_REDIRECT",
    default=False,
)


SECURE_HSTS_SECONDS = env.int(
    "SECURE_HSTS_SECONDS",
    default=0,
)


SESSION_COOKIE_SECURE = env.bool(
    "SESSION_COOKIE_SECURE",
    default=False,
)


CSRF_COOKIE_SECURE = env.bool(
    "CSRF_COOKIE_SECURE",
    default=False,
)


SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "SECURE_CONTENT_TYPE_NOSNIFF",
    default=True,
)


SECURE_REFERRER_POLICY = env(
    "SECURE_REFERRER_POLICY",
    default="strict-origin-when-cross-origin",
)


SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

TELEGRAM_BOT_TOKEN = env(
    "TELEGRAM_BOT_TOKEN",
    default="",
)

TELEGRAM_ADMIN_CHAT_IDS = [
    chat_id.strip()
    for chat_id in env(
        "TELEGRAM_ADMIN_CHAT_IDS",
        default="",
    ).split(",")
    if chat_id.strip()
]

TELEGRAM_WEBHOOK_SECRET = env(
    "TELEGRAM_WEBHOOK_SECRET",
    default="",
)