from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from main import settings

swagger_info = openapi.Info(title="Message Demo API", default_version='v1', description="The Message Demo API")

schema_view = get_schema_view(
    swagger_info,
    public=True,
    permission_classes=(permissions.IsAuthenticatedOrReadOnly,),
)

debug_urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] if settings.DEBUG else []

main_api_paths = [
    path('broker/', include('broker.urls')),
]

urlpatterns = debug_urlpatterns + [
    path('api/v1/', include(main_api_paths))
]
