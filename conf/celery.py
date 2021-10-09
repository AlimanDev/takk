from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

app = Celery('conf')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    # 'task-charge-users-online': {
    #     'task': 'apps.payment.tasks.get_charges_and_capture_online',
    #     'schedule': crontab(),
    #     'args': (),
    # },
    # 'task-charge-users-card': {
    #     'task': 'apps.payment.tasks.get_charges_and_capture_card',
    #     # 'schedule': crontab(hour='*/3', minute='0'),  # каждые 3 три часа
    #     'schedule': crontab(minute='*/10'),  # для теста каздые 10 мин
    #     # 'schedule': crontab(),  # для теста каздые 1 мин
    #     'args': (),
    # },

    # 'task-send-notification-order-acknowledge': {
    #     'task': 'apps.restapi.tasks.send_notification_employee_acknowledge_order',
    #     # 'schedule': crontab(minute='*/5'),  # каждые 5 мин
    #     'schedule': crontab(minute='*/1'),  # для теста каждую минуту
    #     'args': (),
    # },
}