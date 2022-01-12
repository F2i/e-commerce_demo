from django.dispatch import receiver
from store.signals import order_created
from store.models import Customer
from storeMeme import settings


@receiver(signal=order_created)
def on_order_created(sender, **kwargs):
    print(kwargs['order'])
