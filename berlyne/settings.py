"""
Django settings for berlyne project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = "BERLYNE_PRODUCTION" not in os.environ

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_FILE_NAME = ".secret"
SECRET_FILE = os.path.join(BASE_DIR, SECRET_FILE_NAME)


if not os.path.exists(SECRET_FILE):
    open(SECRET_FILE, "wb").write(
        open("/dev/urandom", "rb").read(32)
    )

SECRET_KEY = open(SECRET_FILE, "rb").read()


if DEBUG:
    DOMAIN = "localhost"
else:
    DOMAIN = os.environ["BERLYNE_HOST"]


ALLOWED_HOSTS = [DOMAIN]

ALT_DOMAIN = os.environ.get("BERLYNE_HOST_ALT")

if ALT_DOMAIN:
    ALLOWED_HOSTS.append(ALT_DOMAIN)

LOGFILE = "/tmp/django.log"

if not DEBUG:
    LOGFILE = "/opt/berlyne/log/django.log"
    EMAIL_HOST = "mail.redrocket.club"
    EMAIL_HOST_USER = "system@redrocket.club"
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    try:
        EMAIL_HOST_PASSWORD = open(".email_pw").read().strip()
    except FileNotFoundError:
        print("Email Pw not configured. Emails won't work!")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGFILE
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', "file"],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'),
        },
    },
}


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'vmmanage',
    'wui',
    'autotask'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'berlyne.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'berlyne.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, "berlyne.sqlite3"),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
        }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_ZONE = "Europe/Berlin"

# Flatpages
SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(dir_t, 'static') for temp_list in TEMPLATES for dir_t in temp_list['DIRS']]
STATIC_ROOT = '/var/www/static'
SOUND_FILES = []

# TODO: Add a view/endpoint instead, that returns a random sound as mp3 and ogg
for static_dir in STATICFILES_DIRS:
    _sound_base_dir = os.path.join(static_dir, "sound")
    _sound_dir_mp3 = os.path.join(_sound_base_dir, "mp3")
    _sound_dir_ogg = os.path.join(_sound_base_dir, "ogg")

    if os.path.isdir(_sound_dir_mp3):
        _sounds = os.listdir(_sound_dir_mp3)
        for sound in _sounds:
            if sound.endswith(".mp3"):
                sound_name = os.path.splitext(sound)[0]
                if os.path.isfile(os.path.join(_sound_dir_ogg, sound_name) + ".ogg"):
                    SOUND_FILES.append(sound_name)

# Berlyne specific config
# If this is true, test data will be created

IN_TEST_MODE = DEBUG

# These default actions manage how berlyne treats VMs that
# are/are not used in any course. For compatibility with
# plugins like 'digital ocean' this is start/stop, in
# case you want to drop this compatibility and use
# exclusively VirtualBox/Docker, you can change this
# to "suspend"/"resume" for faster boot times

# Default action to run on VMs when they become unused
DEFAULT_UNUSED_ACTION = "stop"
# Default action to run on VMs that are in use,
# this has to be the opposite of DEFAULT_UNUSED_ACTION
DEFAULT_USED_ACTION = "start"

# autotask
AUTOTASK_IS_ACTIVE = ("makemigrations" not in sys.argv) and ("migrate" not in sys.argv)
AUTOTASK_WORKER_EXECUTABLE = "python3"
# Time the VMs tasks should be stored in the DB
TASK_TTL = 60 * 60 * 24

# uptomate
# Define where the problem folder is
PROBLEM_DEPLOYMENT_PATH = os.path.join(BASE_DIR, 'problems')

