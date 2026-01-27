from django.db   import models

from core.models import TimeStampModel

class Comment(TimeStampModel):
    text = models.CharField(max_length=500)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'comments'

    def __str__(self):
        return self.text