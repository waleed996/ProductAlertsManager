import logging.config
import os
from pathlib import Path

ENV = str(os.getenv('ENV'))

if ENV.lower() == 'local':
    from dotenv import load_dotenv
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('PRODUCT_ALERT_MANAGER_SECRET_KEY')

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # external packages
    "rest_framework",

    # application
    "app",
    
    # for shared data access a separate app
    "shared_data_app"
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'common.exception_helper.custom_exception_handler'
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR],
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
STATIC_URL = "static/"
STATICFILES_DIRS = [str(BASE_DIR) + '/static']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'product_alerts_manager',
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    },
    'products_shared_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'products_information_shared',
        'USER': os.getenv('SHARED_DB_USER'),
        'PASSWORD': os.getenv('SHARED_DB_PASSWORD'),
        'HOST': os.getenv('SHARED_DB_HOST'),
        'PORT': os.getenv('SHARED_DB_PORT'),
    }
}

# Routing for shared db models
DATABASE_ROUTERS = ['config.db_routing.SharedDbRouter']

# Custom Logging Config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'app': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'shared_data_app': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
})

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ALLOWED_HOSTS = ['*']

DEBUG = bool(os.getenv('DEBUG', False))

# CELERY
CELERY_BROKER_URL = os.getenv('REDIS_BROKER_URL')
CELERY_USER_PRODUCT_EMAIL_WORKER_BATCH_SIZE = int(os.getenv('CELERY_USER_PRODUCT_EMAIL_WORKER_BATCH_SIZE', 500))
CELERY_BEAT_TASK_ENQUEUE_PERIOD_SECONDS = int(os.getenv('CELERY_BEAT_TASK_ENQUEUE_PERIOD_SECONDS'))

# REDIS CACHE URL
REDIS_CACHE_URL = os.getenv('REDIS_CACHE_URL')
REDIS_EBAY_ACCESS_TOKEN_KEY_NAME = 'EBAY_ACCESS_TOKEN'

# REDIS QUEUE
REDIS_QUEUE_URL = os.getenv('REDIS_QUEUE_URL')
REDIS_USER_SETTINGS_QUEUE = os.getenv('REDIS_USER_SETTINGS_QUEUE')

# Email Settings, using just a simple solution for email for now
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('PRODUCT_UPDATES_SENDER_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('PRODUCT_UPDATES_SENDER_EMAIL_PASSWORD')

# Ebay
EBAY_ENDPOINT_BASE_URL = os.getenv('EBAY_ENDPOINT_BASE_URL')
EBAY_BASIC_AUTH_USERNAME = os.getenv('EBAY_BASIC_AUTH_USERNAME')
EBAY_BASIC_AUTH_PASSWORD = os.getenv('EBAY_BASIC_AUTH_PASSWORD')
