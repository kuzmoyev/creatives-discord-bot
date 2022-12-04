from pathlib import Path
from os import getenv
from urllib.parse import urljoin

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv('SECRET_KEY')

# Discord
DISCORD_TOKEN = getenv('DISCORD_TOKEN')
GUILD_ID = int(getenv('GUILD_ID'))
BOT_ALERTS_CHANNEL = int(getenv('BOT_ALERTS_CHANNEL'))
GENERAL_CHANNEL = int(getenv('GENERAL_CHANNEL'))
SUBMISSIONS_CHANNEL = int(getenv('SUBMISSIONS_CHANNEL'))

DISCORD_URL = 'https://discord.com'
DISCORD_CHANNELS_URL = urljoin(DISCORD_URL, 'channels/')
DISCORD_GUILD_URL = urljoin(DISCORD_CHANNELS_URL, str(GUILD_ID) + '/')
DISCORD_SUBMISSION_URL = urljoin(DISCORD_GUILD_URL, str(SUBMISSIONS_CHANNEL) + '/')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv('DEBUG', False).lower() == 'true'

ALLOWED_HOSTS = getenv('DJANGO_ALLOWED_HOSTS').split()

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'admin_reorder',

    'bot'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'bot.middleware.ModelAdminReorderWithNav'
]

ROOT_URLCONF = 'creatives_discord_bot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'creatives_discord_bot.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": getenv("DATABASE_ENGINE", "django.db.backends.sqlite3"),
        "NAME": getenv("POSTGRES_DB", BASE_DIR / "db.sqlite3"),
        "USER": getenv("POSTGRES_USER", "user"),
        "PASSWORD": getenv("POSTGRES_PASSWORD", "password"),
        "HOST": getenv("POSTGRES_HOST", "localhost"),
        "PORT": getenv("POSTGRES_PORT", "5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_ROOT = 'static'
STATIC_URL = 'static/'
IMAGES_URL = 'images/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMIN_REORDER = (
    'sites',
    {
        'app': 'bot',
        'label': 'Users',
        'models': (
            'bot.User',
        )
    },
    {
        'app': 'bot',
        'label': 'Challenges',
        'models': (
            'bot.Challenge',
            'bot.InspirationImage',
        )
    },
    {
        'app': 'bot',
        'label': 'Submissions',
        'models': (
            'bot.Submission',
            'bot.Vote',
        )
    },
)
