import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery = Celery('config')
celery.config_from_object(settings, namespace='CELERY')

celery.conf.beat_schedule = {
    'send_user_product_alerts': {
        'task': 'app.tasks.user_product_email_task_distributor',
        'schedule': settings.CELERY_BEAT_TASK_ENQUEUE_PERIOD_SECONDS
    }
}

celery.autodiscover_tasks()

