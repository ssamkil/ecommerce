from django.db   import models

from core.models import TimeStampModel

class User(TimeStampModel):
    name     = models.CharField(max_length=100, default='')
    email    = models.CharField(max_length=200)
    password = models.CharField(max_length=200)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name