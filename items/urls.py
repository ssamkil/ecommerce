from django.urls import path, include
from .views      import *

urlpatterns = [
    path('', ItemListView.as_view()),
    path('<int:item_id>/', ItemDetailView.as_view()),
    path('search/', SearchItemView.as_view()),
    path('review/', ReviewView.as_view()),
]