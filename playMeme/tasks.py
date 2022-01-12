from time import sleep
from celery import shared_task

@shared_task
def notify_customers(mess, *args, **kwargs):
    print('Starting sending...')
    sleep(5)
    print('Mail sending completed!')