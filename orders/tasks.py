from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from .models import Order, OrderItem, OrderStatus

@shared_task
def terminate_expired_orders():
    raise ValueError("Celery Sentry Test")

    limit_time = timezone.now() - timedelta(minutes=60)

    expired_orders = Order.objects.filter(
        order_status_id = OrderStatus.Status.PENDING,
        created_at__lt  = limit_time
    )

    for order in expired_orders:
        with transaction.atomic():
            order_items = OrderItem.objects.filter(order=order).select_related('item')
            for order_item in order_items:
                item = order_item.item
                item.quantity += order_item.quantity
                item.save()

            order.order_status_id = OrderStatus.Status.DECLINED
            order.save()

    return f"TERMINATING {expired_orders.count()} ORDERS"