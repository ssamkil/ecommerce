from django.urls import path
from posts.views import *

urlpatterns = [
    path('', PostView.as_view()),
]