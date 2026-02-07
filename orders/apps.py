from django.apps              import AppConfig
from django.db.models.signals import post_migrate

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        post_migrate.connect(create_initial_order_status, sender=self)

def create_initial_order_status(sender, **kwargs):
    from .models import OrderStatus

    status = [
        {'id': 1, 'status': 'PENDING'},
        {'id': 2, 'status': 'COMPLETED'},
        {'id': 3, 'status': 'DECLINED'}
    ]

    for s in status:
        OrderStatus.objects.get_or_create(id=s['id'], defaults={'status': s['status']})