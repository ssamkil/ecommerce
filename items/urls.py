from django.urls import path, include
from .views      import *

urlpatterns = [
    path('', ItemView.as_view()),
    path('/<int:item_id>', ItemView.as_view()),
    path('/search', SearchItemView.as_view()),
    path('/review', ReviewView.as_view())
]