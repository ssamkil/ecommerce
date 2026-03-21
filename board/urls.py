from django.contrib          import admin
from django.urls             import path, include
from rest_framework          import permissions
from drf_yasg.views          import get_schema_view
from drf_yasg                import openapi
from drf_spectacular.views   import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

schema_view = get_schema_view(
    openapi.Info(
        title="Ecommerce API",
        default_version='v1',
        description="Ecommerce API Document",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('posts/', include('posts.urls')),
    path('items/', include('items.urls')),
    path('carts/', include('carts.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('allauth.urls')),
    path('comments/', include('comments.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

] # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
