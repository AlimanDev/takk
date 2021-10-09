from django.urls import path, re_path
from apps.restapi.tablet import views as tablet_views


app_name = 'tablet'
urlpatterns = [
    path('ckeck/cafe/<int:pk>/category/', tablet_views.ProductCategoryCheckView.as_view()),
    path('ckeck/cafe/<int:pk>/sub-category/', tablet_views.ProductSubCategoryCheckView.as_view()),
    path('ckeck/cafe/<int:pk>/product/', tablet_views.ProductCheckView.as_view()),
    path('ckeck/cafe/<int:pk>/modifier-item/', tablet_views.ProductModifierItemCheckView.as_view()),
    path('ckeck/cafe/<int:pk>/modifier/', tablet_views.ProductModifierCheckView.as_view()),
    path('ckeck/cafe/<int:pk>/size/', tablet_views.ProductSizeCheckView.as_view()),
    path('order/', tablet_views.OrderCreateView.as_view()),

    # API FOR TERMINAL CONNECT
    path('terminal/payment/order/<int:pk>/', tablet_views.OrderPaymentView.as_view()),
    path('terminal/finish-payment/', tablet_views.FinishOrderPaymentView.as_view()),
    path('terminal/location/', tablet_views.CreateLocationForTerminalView.as_view()),
    path('terminal/token/', tablet_views.CreateTokenForTerminalView.as_view()),



]