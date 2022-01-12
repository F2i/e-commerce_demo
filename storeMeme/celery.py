import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeMeme.settings.dev')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

celery = Celery()
celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()