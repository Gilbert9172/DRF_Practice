#-- Django
from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

#-- DRF
from rest_framework import permissions

#-- yasg
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

#-- JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


schema_view = get_schema_view(
    openapi.Info(
        title="drfAPI 연습",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.ourapp.com/policies/terms/",
        contact=openapi.Contact(email="contact@expenses.local"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    # path('expenses/', include('expenses.urls')),
    # path('income/', include('income.urls')),
    path('posts/', include('posts.urls')),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name="schema-json"),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
