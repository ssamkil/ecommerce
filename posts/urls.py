from django.urls import path
from posts.views import *

urlpatterns = [
    path('', PostView.as_view()),
    path('/postList/<int:page_num>', PostListView.as_view())
]