from django.urls import path, re_path
from apps.restapi.dashboard import views as dashboard_view


app_name = 'dashboard'

urlpatterns = [

    # AUTH
    path('login/', dashboard_view.LoginView.as_view()),
    path('phone-verified/', dashboard_view.UserPhoneVerifiedView.as_view()),
    path('register-company-owner/', dashboard_view.RegisterCompanyOwnerView.as_view()),
    path('user-profile/', dashboard_view.UserProfileView.as_view()),
    path('customer/list/', dashboard_view.CustomerListView.as_view()),

    # Cafe
    path('cafe/<int:pk>/', dashboard_view.CafeRetrieveUpdateDestroyView.as_view()),
    path('cafe/list/', dashboard_view.CafeListView.as_view()),


    path('company/settings/', dashboard_view.CompanySettingView.as_view()),
    path('company/all/', dashboard_view.CompanyAllListView.as_view()),
    path('company/<int:pk>/', dashboard_view.CompanyRetrieveView.as_view()),
    path('company/employee/', dashboard_view.CompanyEmployeeView.as_view()),
    path('company/order-transaction/', dashboard_view.OrderTransactionView.as_view()),
    path('company/budget-transaction/', dashboard_view.BudgetTransactionView.as_view()),


    path('menu/<int:pk>/products/', dashboard_view.MenuProductsListView.as_view()),
    path('menu/<int:pk>/categories/', dashboard_view.MenuProductCategoryListView.as_view()),
    path('menu/<int:pk>/modifiers/', dashboard_view.MenuModifiersListView.as_view()),

    path('product/modifier-item/<int:pk>/', dashboard_view.ModifierItemRetrieveUpdateDestroyView.as_view()),
    path('product/modifier-item/', dashboard_view.ModifierItemCreateView.as_view()),
    path('product/modifier/<int:pk>', dashboard_view.ModifierRetrieveUpdateDestroyView.as_view()),
    path('product/modifier/', dashboard_view.ModifierCreateView.as_view()),
    path('product/category/<int:pk>', dashboard_view.ProductCategoryRetrieveUpdateDestroyView.as_view()),
    path('product/category/', dashboard_view.ProductCategoryCreateView.as_view()),
    path('product/<int:pk>', dashboard_view.ProductRetrieveUpdateDestroyView.as_view()),
    path('product/', dashboard_view.ProductCreateView.as_view()),


]