from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from conf.swagger_conf import (
    schema_view_mobile,
    schema_view_dashboard,
    schema_view_tablet,
    schema_view_mobile_v2,
    schema_view_dashboard_v2,
    schema_view_tablet_v2,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('payment/', include('apps.payment.urls')),  # TODO: для теста stripe webhook
    # API V1
    path('api/v1/tablet/', include('apps.restapi.tablet.urls', namespace='swagger_tablet')),
    path('api/v1/mobile/', include('apps.restapi.mobile.urls', namespace='swagger_mobile')),
    path('api/v1/dashboard/', include('apps.restapi.dashboard.urls', namespace='swagger_dashboard')),

    # API V2
    path('api/v2/tablet/', include('apps.restapi_v2.tablet.urls', namespace='swagger_tablet_v2')),
    path('api/v2/mobile/', include('apps.restapi_v2.mobile.urls', namespace='swagger_mobile_v2')),
    path('api/v2/dashboard/', include('apps.restapi_v2.dashboard.urls', namespace='swagger_dashboard_v2')),

    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

]

urlpatterns += [
    # Tablet swagger url
    re_path(r'^swagger/tablet(?P<format>\.json|\.yaml)$', schema_view_tablet.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/tablet/$', schema_view_tablet.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^swagger/tablet/docs/$', schema_view_tablet.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Mobile swagger url
    re_path(r'^swagger/mobile(?P<format>\.json|\.yaml)$', schema_view_mobile.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/mobile/$', schema_view_mobile.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^swagger/mobile/docs/$', schema_view_mobile.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Dashboard swagger url
    re_path(r'^swagger/dashboard(?P<format>\.json|\.yaml)$', schema_view_dashboard.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/dashboard/$', schema_view_dashboard.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^swagger/dashboard/docs/$', schema_view_dashboard.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Tablet_v2 swagger url
    re_path(r'^swagger/tablet/v2(?P<format>\.json|\.yaml)$', schema_view_tablet_v2.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/tablet/v2/$', schema_view_tablet_v2.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^swagger/tablet/docs/v2/$', schema_view_tablet_v2.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Mobile_v2 swagger url
    re_path(r'^swagger/mobile/v2(?P<format>\.json|\.yaml)$', schema_view_mobile_v2.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/mobile/v2/$', schema_view_mobile_v2.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^swagger/mobile/docs/v2/$', schema_view_mobile_v2.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Dashboard_v2 swagger url
    re_path(r'^swagger/dashboard/v2(?P<format>\.json|\.yaml)$', schema_view_dashboard_v2.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/dashboard/v2/$', schema_view_dashboard_v2.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^swagger/dashboard/docs/v2/$', schema_view_dashboard_v2.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


