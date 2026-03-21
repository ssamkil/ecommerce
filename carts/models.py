from django.db    import models
from core.models  import TimeStampModel

class Cart(TimeStampModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'carts'