from django.urls import path
from .views      import *

urlpatterns = [
    path('', CommentView.as_view()),
    path('/<int:post_id>', CommentView.as_view()),
]