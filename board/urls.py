import requests
from django.contrib          import admin
from django.urls             import path, include
from django.conf             import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin', admin.site.urls),
    path('users', include('users.urls')),
    path('posts', include('posts.urls')),
    path('items', include('items.urls')),
    path('carts', include('carts.urls')),
    path('orders', include('orders.urls')),
    path('accounts/', include('allauth.urls')),
    path('comments', include('comments.urls'))
] # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
