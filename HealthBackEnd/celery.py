from celery import Celery

app = Celery('HealthBackEnd')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from celery.schedules import crontab
