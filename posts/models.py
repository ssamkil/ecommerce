from django.db   import models
from core.models import TimeStampModel

class Post(TimeStampModel):
    title = models.CharField(max_length=100)
    body  = models.TextField()
    user  = models.ForeignKey('users.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'posts'

    def __str__(self):
        return self.title