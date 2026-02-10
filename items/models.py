from django.db    import models

from core.models  import TimeStampModel

class Item(TimeStampModel):
    category    = models.ForeignKey('Category', on_delete=models.CASCADE)
    name        = models.CharField(max_length=200)
    price       = models.FloatField()
    quantity    = models.PositiveSmallIntegerField()
    image       = models.ImageField(upload_to='', null=True, blank=True)

    class Meta:
        db_table = 'items'

    def __str__(self):
        return self.name

class Category(models.Model):
    name      = models.CharField(max_length=100)
    thumbnail = models.URLField(max_length=400, blank=True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name

class Review(TimeStampModel):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    body = models.CharField(max_length=1000)

    class Meta:
        db_table = 'reviews'

    def __str__(self):
        return self.body