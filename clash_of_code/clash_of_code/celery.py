import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clash_of_code.settings')

app = Celery('clash_of_code')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
