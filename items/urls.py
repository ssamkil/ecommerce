from django.urls import path, include
from .views      import *

urlpatterns = [
    path('', ItemView.as_view()),
]