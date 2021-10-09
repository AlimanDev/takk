from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.restapi.mobile.urls import urlpatterns as mobile_urlpatterns
from apps.restapi.dashboard.urls import urlpatterns as dashboard_urlpatterns
from apps.restapi.tablet.urls import urlpatterns as tablet_urlpatterns
from apps.restapi_v2.mobile.urls import urlpatterns as mobile_urlpatterns_v2
from apps.restapi_v2.dashboard.urls import urlpatterns as dashboard_urlpatterns_v2
from apps.restapi_v2.tablet.urls import urlpatterns as tablet_urlpatterns_v2


# Mobile swagger v1
schema_view_mobile = get_schema_view(
   openapi.Info(
      title="Takk mobile api",
      default_version='v1',

   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   patterns=[
       re_path(r'api/v1/mobile/', include(mobile_urlpatterns))
   ]

)


# Dashboard swagger v1
schema_view_dashboard = get_schema_view(
   openapi.Info(
      title="Takk dashboard api",
      default_version='v1',

   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   patterns=[
       re_path(r'api/v1/dashboard/', include(dashboard_urlpatterns))
   ]

)

# Tablet swagger v1
schema_view_tablet = get_schema_view(
   openapi.Info(
      title="Takk tablet api",
      default_version='v1',

   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   patterns=[
       re_path(r'api/v1/tablet/', include(tablet_urlpatterns))
   ]

)

# Mobile swagger v2
schema_view_mobile_v2 = get_schema_view(
   openapi.Info(
      title="Takk mobile api",
      default_version='v2',

   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   patterns=[
       re_path(r'api/v2/mobile/', include(mobile_urlpatterns_v2))
   ]

)


# Dashboard swagger v2
schema_view_dashboard_v2 = get_schema_view(
   openapi.Info(
      title="Takk dashboard api",
      default_version='v2',

   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   patterns=[
       re_path(r'api/v2/dashboard/', include(dashboard_urlpatterns_v2))
   ]

)

# Tablet swagger v2
schema_view_tablet_v2 = get_schema_view(
   openapi.Info(
      title="Takk tablet api",
      default_version='v2',

   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   patterns=[
       re_path(r'api/v2/tablet/', include(tablet_urlpatterns_v2))
   ]

)