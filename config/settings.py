from pathlib import Path
import os
import sys

import environ

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
db_mode = env("DB_MODE", default="sqlite")

INSTALLED_APPS = [
    "common",
]

MIDDLEWARE = []

if db_mode == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    db_ssl_ca = env("DB_SSL_CA", default="/etc/ssl/certs/rds-global-bundle.pem")
    db_use_ssl = env.bool("DB_USE_SSL", default=True)
    mysql_options = {"charset": "utf8mb4"}
    if db_use_ssl:
        mysql_options["ssl"] = {"ca": db_ssl_ca}

    DATABASES = {
        "posts_db": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["DB_NAME_POSTS"],
            "USER": os.environ["DB_USER_POSTS"],
            "PASSWORD": os.environ["DB_PASSWORD_POSTS"],
            "HOST": os.environ["DB_HOST"],
            "PORT": "3306",
            "OPTIONS": mysql_options.copy(),
        },
        "auth_db": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["DB_NAME_AUTH"],
            "USER": os.environ["DB_USER_AUTH"],
            "PASSWORD": os.environ["DB_PASSWORD_AUTH"],
            "HOST": os.environ["DB_HOST"],
            "PORT": "3306",
            "OPTIONS": mysql_options.copy(),
        },
        "events_db": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["DB_NAME_EVENTS"],
            "USER": os.environ["DB_USER_EVENTS"],
            "PASSWORD": os.environ["DB_PASSWORD_EVENTS"],
            "HOST": os.environ["DB_HOST"],
            "PORT": "3306",
            "OPTIONS": mysql_options.copy(),
        },
    }
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

APPEND_SLASH = False

AWS_REGION = env("AWS_REGION", default=env("AWS_DEFAULT_REGION", default="ap-northeast-2"))
NOTIFICATION_EVENT_BUS_NAME = env("NOTIFICATION_EVENT_BUS_NAME", default="stagelog-notification-bus")
OUTBOX_PUBLISH_BATCH_SIZE = env.int("OUTBOX_PUBLISH_BATCH_SIZE", default=50)
OUTBOX_MAX_RETRIES = env.int("OUTBOX_MAX_RETRIES", default=5)
OUTBOX_RETRY_BASE_DELAY_SECONDS = env.int("OUTBOX_RETRY_BASE_DELAY_SECONDS", default=30)
OUTBOX_DATABASES = env.list("OUTBOX_DATABASES", default=["posts_db", "auth_db", "events_db"])
