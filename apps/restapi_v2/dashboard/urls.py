from django.urls import path, re_path
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter
from django.urls import include
from apps.restapi_v2.dashboard import views

app_name = 'dashboard_v2'

urlpatterns = [
    path('users/devices/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'})),
    path('users/login/', views.LoginAPiView.as_view()),
    path('users/profile/', views.UserProfileAPIView.as_view()),

    path('companies/<int:pk>/menus/<int:menu_id>/', views.CompanyUpdateDeleteAPIView.as_view()),
    path('companies/<int:pk>/menus/', views.CompanyMenuListAPIView.as_view()),
    path('companies/<int:pk>/', views.CompanyUpdateAPIView.as_view()),
    path('companies/', views.CompanyListAPIView.as_view()),
    path('cafes/<int:pk>/', views.CafeUpdateAPIView.as_view()),
    path('menus/<int:pk>/products/', views.MenuProductsListView.as_view()),
    path('menus/<int:pk>/categories/', views.MenuProductCategoryListView.as_view()),
    path('menus/<int:pk>/modifiers/', views.MenuModifiersListView.as_view()),
    path('menus/products-ordering/', views.SortedMenuProductsAPIView.as_view()),

    path('products/modifier-items/<int:pk>/', views.ModifierItemRetrieveUpdateDestroyView.as_view()),
    path('products/modifier-items/', views.ModifierItemCreateView.as_view()),
    path('products/modifiers/<int:pk>', views.ModifierRetrieveUpdateDestroyView.as_view()),
    path('products/modifiers/', views.ModifierCreateView.as_view()),
    path('products/categories/<int:pk>', views.ProductCategoryRetrieveUpdateDestroyView.as_view()),
    path('products/categories/', views.ProductCategoryCreateView.as_view()),
    path('products/<int:pk>/', views.ProductRetrieveUpdateDestroyView.as_view()),
    path('products/', views.ProductCreateView.as_view()),

]

