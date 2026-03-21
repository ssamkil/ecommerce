from django.db    import models
from core.models  import TimeStampModel

class Order(TimeStampModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    order_status = models.ForeignKey('OrderStatus', on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    order_number = models.CharField(max_length=150, unique=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return self.order_number

class OrderItem(TimeStampModel):
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'order_items'

class OrderStatus(models.Model):
    class Status(models.IntegerChoices):
        PENDING   = 1
        COMPLETED = 2
        DECLINED  = 3

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    class Meta:
        db_table = 'order_status'