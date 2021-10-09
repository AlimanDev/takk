from django.urls import path, re_path
from apps.restapi.mobile import client_views, employee_views
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter
from django.urls import include

app_name = 'mobile'
urlpatterns = [

    path('cart/favorite/list/', client_views.FavoriteCartListView.as_view()),
    path('cart/favorite/<int:pk>/', client_views.FavoriteCartUpdateDestroyView.as_view()),
    path('cart/favorite/', client_views.FavoriteCartCreateView.as_view()),
    path('cart/favorite/item/<int:pk>/', client_views.FavoriteCartItemUpdateDestroyView.as_view()),

    path('cart/item/<int:pk>/', client_views.CartItemUpdateDestroyView.as_view()),
    path('cart/item/', client_views.CartItemCreateView.as_view()),
    path('cart/empty/', client_views.CartEmptyView.as_view()),
    path('cart/add-tip/', client_views.CartAddTipView.as_view()),
    path('cart/', client_views.CartView.as_view()),

    path('devices/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'})),

    path('user/card/list/', client_views.UserCardListView.as_view()),
    path('user/card/add/', client_views.UserSaveCardView.as_view()),
    path('user/card/<int:pk>/', client_views.UserCardUpdateDeleteView.as_view()),
    path('user/login/', client_views.RegisterLoginUserView.as_view()),
    path('user/free-items/', client_views.UserFreeItemsView.as_view()),
    path('user/points/', client_views.UserPointsList.as_view()),
    path('user/budget-fill-history/', client_views.UserBalanceFillHistory.as_view()),
    path('user/notifications/', client_views.UserNotificationView.as_view()),
    path('user/', client_views.UserRetrieveUpdateView.as_view()),

    path('favorite-cart/<int:pk>/to-cart/', client_views.FavoriteCartToCartView.as_view()),
    path('order/<int:pk>/to-cart/', client_views.OrderToCartView.as_view()),
    # path('order/cart/', client_views.PaymentOrderView.as_view()),
    path('order/ckeck-order-limit/<int:pk>', client_views.CheckOrderLimitView.as_view()),
    path('order/user-orders/', client_views.OrderListView.as_view()),
    path('cafe/<int:pk>/product_list/', client_views.CafeProductsView.as_view()),

    path('cafe/<int:pk>/change-favorite/', client_views.CafeChangeFavorite.as_view()),
    path('cafe/<int:pk>/', client_views.CafeDetailView.as_view()),
    path('cafe/', client_views.CafeListView.as_view()),


    path('company/<int:pk>/', client_views.CompanyRetrieveView.as_view()),
    path('company/list/', client_views.CompanyListView.as_view()),

    # path('cafe/<int:pk>/others/', client_views.CompanyCafesView.as_view()),
    path('tariff/payment/', client_views.TopUpBalanceView.as_view()),
    path('tariff/list/', client_views.TariffListView.as_view()),

    path('refund/order/<int:pk>/', employee_views.RefundPaymentOrderView.as_view()),
    path('employee/cafe/list/', employee_views.EmployeeCafesListView.as_view()),
    path('employee/order/<int:pk>/status/', employee_views.EmployeeUpdateOrderStatusView.as_view()),
    path('employee/order/<int:pk>/acknowledge/', employee_views.OrderAcknowledgeView.as_view()),
    path('employee/order/<int:pk>/', employee_views.EmployeeCafeOrderDetailView.as_view()),
    path('employee/orders/', employee_views.EmployeeCafeOrdersView.as_view()),
    # path('employee/product/<int:pk>/status/', employee_views.EmployeeProductStatusUpdateView.as_view()),
    path('employee/from-kitchen/', employee_views.ReadyKitchenOrderItemView.as_view()),
    path('employee/from-main/', employee_views.ReadyMainOrderItemView.as_view()),
    path('employee/give-points/', employee_views.EmployeeGivePointToCustomerView.as_view()),
]

