from django.urls import path, re_path
from apps.restapi_v2.mobile import views
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter
from django.urls import include

app_name = 'mobile_v2'
urlpatterns = [
    path('users/auth/', views.UserAuthAPIView.as_view()),
    path('users/device/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'})),
    path('users/cards/add/', views.UserSaveCardAPIView.as_view()),
    path('users/cards/<int:pk>/', views.UserCardUpdateDeleteAPIView.as_view()),
    path('users/cards/', views.UserCardListAPIView.as_view()),
    path('users/profile/', views.UserProfileAPIView.as_view()),
    path('users/points/', views.UserPointAPIView.as_view()),
    path('users/notifications/', views.UserNotificationAPIView.as_view()),
    path('users/free-items/', views.UserFreeItemsAPIView.as_view()),
    path('users/balance-fill-history/', views.UserBalanceFillHistoryAPIView.as_view()),
    path('users/top-up-balance/', views.UserTopUpBalanceAPIView.as_view()),
    path('users/favorite-cafe/<int:pk>/', views.UserFavoriteCafeAPIView.as_view()),

    path('carts/item/<int:pk>/', views.CartItemUpdateDestroyAPIView.as_view()),
    path('carts/item/', views.CartItemCreateAPIView.as_view()),
    path('carts/empty/', views.CartEmptyAPIView.as_view()),
    path('carts/tip/', views.CartAddTipAPIView.as_view()),
    path('carts/order/', views.CartOrderAPIView.as_view()),
    path('carts/', views.UserCartAPIView.as_view()),

    path('favorite-carts/item/<int:pk>/', views.FavoriteCartItemUpdateDestroyAPIView.as_view()),
    path('favorite-carts/<int:pk>/to-cart/', views.FavoriteCartToCartAPIView.as_view()),
    path('favorite-carts/<int:pk>/', views.FavoriteCartUpdateDestroyAPIView.as_view()),
    path('favorite-carts/', views.FavoriteCartAPIView.as_view()),

    path('orders/<int:pk>/to-cart/', views.OrderToCartAPIView.as_view()),
    path('orders/check-order-limit/<int:pk>/', views.CheckOrderLimitAPIView.as_view()),
    path('orders/list/', views.UserOrderListAPIView.as_view()),

    path('companies/<int:pk>/', views.CompanyRetrieveAPIView.as_view()),
    path('companies/', views.CompanyListAPIView.as_view()),

    path('takk/tariffs/', views.TariffListView.as_view()),

    path('cafes/<int:pk>/product-list/', views.CafeProductsAPIView.as_view()),
    path('cafes/<int:pk>/', views.CafeDetailAPIView.as_view()),
    path('cafes/', views.CafeListAPIView.as_view()),

    # path('refund/order/<int:pk>/', employee_views.RefundPaymentOrderView.as_view()),
    path('employees/cafes/product-available/', views.CafeProductAvailableAPIView.as_view()),
    path('employees/orders/item/ready/', views.ReadyOrderItemAPIView.as_view()),
    path('employees/orders/<int:pk>/status/', views.EmployeeUpdateOrderStatusAPIView.as_view()),
    path('employees/orders/<int:pk>/acknowledge/', views.OrderAcknowledgeAPIView.as_view()),
    path('employees/orders/<int:pk>/', views.EmployeeCafeOrderDetailAPIView.as_view()),
    path('employees/orders/', views.EmployeeCafeOrdersAPIView.as_view()),
    path('employees/give-points/', views.EmployeeGivePointToCustomerAPIView.as_view()),
    path('employees/cafes/', views.EmployeeCafesListAPIView.as_view()),

]