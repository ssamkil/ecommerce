from django.db   import models

from core.models import TimeStampModel

class Comment(TimeStampModel):
    text = models.CharField(max_length=500)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'comments'

    def delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.text[:20] + '...'