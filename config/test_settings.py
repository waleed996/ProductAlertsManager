

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "rest_framework",
    "app"
]

# Get secret from secret store from cloud
SECRET_KEY = "django-insecure-l6mhdpf^ae=9unx$)0(ijr_&7^#ze$kwn*6v6pqznt-sa=64*f"

# Get secrets from secret store from cloud
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'product_alerts_manager',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

ROOT_URLCONF = "config.urls"
USE_TZ = False

CELERY_BEAT_TASK_ENQUEUE_PERIOD_SECONDS = None

# Set the redis queue url here e.g. redis://127.0.0.1:6379/2
REDIS_QUEUE_URL = ''
