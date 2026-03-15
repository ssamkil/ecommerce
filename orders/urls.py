from django.urls import path, include
from .views      import *

urlpatterns = [
    path('', include([
        path('', OrderView.as_view()),
        path('<int:order_id>/', OrderView.as_view())
    ])),
]