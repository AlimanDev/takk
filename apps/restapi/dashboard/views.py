from random import randint

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, serializers, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework_tracking.mixins import LoggingMixin

from django_filters import rest_framework as django_filters
from django.contrib.auth.hashers import check_password
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from apps.users import models as user_models
from apps.users import logics as user_logics
from apps.restapi import permissions as my_permissions
from apps.restapi.pagination import MyPagination
from apps.restapi import exceptions as my_exception
from apps.restapi.dashboard import views_logic
from apps.restapi.dashboard import serializers as dashboard_serializer

from apps.companies import models as company_models
from apps.orders import models as order_models
from apps.products import models as product_models
from apps.payment import models as payment_models


class LoginView(LoggingMixin, generics.GenericAPIView):
    """ Авторизация
    status = 0 -> ошибка (неверный пароль, ошибка при валидации, или нет такого пользователя)
    message -> описано какая ошибка
    status = 1 -> Пользователь не верефицировал свой номер телефона (нужно показать
    для клиента форму для потвердения смс кода)
    status = 2 -> вернет токены в data
    status = 3 -> ошибка
    """
    queryset = user_models.User.objects.all()
    serializer_class = dashboard_serializer.LoginSerializer
    permission_classes = (permissions.AllowAny, )
    http_method_names = ('post', )
    logging_methods = ('POST', )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        response_data = {}
        user = views_logic.get_user(request.data.get('phone', False))

        if not serializer.is_valid(raise_exception=False):
            response_data['message'] = 'Invalid data'
            response_data['status'] = 0
            response_data['data'] = {}

        elif not user:
            response_data['message'] = 'Invalid phone'
            response_data['status'] = 0
            response_data['data'] = {}

        elif not user.check_password(serializer.validated_data.get('password')):
            response_data['message'] = 'Invalid password'
            response_data['status'] = 0
            response_data['data'] = {}

        elif not user.phone_is_verified:
            response_data['message'] = 'Your phone number was not verified'
            response_data['data'] = {}
            response_data['status'] = 1

        elif user and user.check_password(serializer.validated_data.get('password')) and user.phone_is_verified:
            response_data['message'] = 'Success'
            response_data['status'] = 2
            token = user_logics.get_tokens_for_user(user)
            response_data['data'] = {
                'refresh': token.get('refresh'),
                'access': token.get('access')
            }
        else:
            response_data['message'] = 'error'
            response_data['data'] = {}
            response_data['status'] = 3

        return Response(data=response_data, status=status.HTTP_200_OK)


class UserPhoneVerifiedView(LoggingMixin, generics.GenericAPIView):
    """ Потвердить номер телефона если отправить только номер отправит смс на номер (123456 для теста)
        status = 0 -> Invalid data или Invalid sms code
        status = 1 -> Sms код был отправлен на номер
        status = 2 -> вернет токен в data
        status = 3 -> Ошибка
    """
    queryset = user_models.User.objects.all()
    serializer_class = dashboard_serializer.UserPhoneVerifiedSerializer
    permission_classes = (permissions.AllowAny, )
    http_method_names = ('post',)
    logging_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        response_data = {}
        user = views_logic.get_user(request.data.get('phone', False))

        if serializer.is_valid(raise_exception=False):
            response_data['message'] = 'Invalid data'
            response_data['status'] = 0
            response_data['data'] = {}

        elif user and serializer.validated_data.get('sms_code'):
            if user.sms_code == serializer.validated_data.get('sms_code'):
                response_data['message'] = 'Success'
                response_data['status'] = 2
                token = user_logics.get_tokens_for_user(user)
                user.phone_is_verified = True
                user.save(update_fields=['phone_is_verified', ])
                response_data['data'] = {
                    'refresh': token.get('refresh'),
                    'access': token.get('access')
                }
            else:
                response_data['message'] = 'Invalid sms code'
                response_data['status'] = 0
                response_data['data'] = {}

        elif user and not serializer.validated_data.get('sms_code'):
            user_logics.send_sms(user)
            response_data['message'] = 'Send sms code'
            response_data['status'] = 1
            response_data['data'] = {}
        else:
            response_data['message'] = 'error'
            response_data['status'] = 3
            response_data['data'] = {}

        return Response(data=response_data, status=status.HTTP_200_OK)


class RegisterCompanyOwnerView(LoggingMixin, generics.CreateAPIView):
    queryset = user_models.User.objects.all()
    serializer_class = dashboard_serializer.CompanyOwnerCreateSerializer
    permission_classes = [permissions.AllowAny]
    logging_methods = ('POST',)


class CompanySettingView(LoggingMixin, generics.RetrieveUpdateAPIView):
    """"""
    queryset = company_models.Company.objects.all()
    serializer_class = dashboard_serializer.CompanySerializer
    permission_classes = (permissions.AllowAny, )  # TODO изменить
    logging_methods = ('GET', 'PUT', 'PATCH')

    def get_object(self):  # TODO для теста
        obj = company_models.Company.objects.all().first()
        return obj


class CafeListView(LoggingMixin, generics.ListAPIView):
    """  Список кафе компании
    status: BLOCKED = 0 ACTIVE = 1 PENDING = 2"""
    queryset = company_models.Cafe.objects.all()
    serializer_class = dashboard_serializer.CafeListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = MyPagination
    logging_methods = ('GET',)


class CafeRetrieveUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """  Получить/обновить/удалить кафе компании"""
    queryset = company_models.Company.objects.all()
    serializer_class = dashboard_serializer.CafeSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('GET', 'PUT', 'DELETE')
    http_method_names = ('get', 'put', 'delete')

    def get_queryset(self):  # TODO изменить
        cafes = company_models.Cafe.objects.all()
        return cafes


class MenuProductsListView(LoggingMixin, generics.ListAPIView):
    """ Товары меню"""
    queryset = product_models.Product.objects.all()
    serializer_class = dashboard_serializer.ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = MyPagination
    logging_methods = ('GET',)
    filterset_fields = ('category', 'category__parent')
    search_fields = ('name',)

    def get_queryset(self):
        queryset = super().get_queryset().filter(category__menu=self.get_object())
        return queryset

    def get_object(self):
        try:
            menu = company_models.Menu.objects.get(id=self.kwargs.get(self.lookup_field))
            return menu
        except company_models.Menu.DoesNotExist:
            raise NotFound('menu does not exist')


class MenuProductCategoryListView(LoggingMixin, generics.ListAPIView):
    """ Список категорий (вложенный список)"""
    queryset = product_models.ProductCategory.objects.all()
    serializer_class = dashboard_serializer.ProductCategoryCreateListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = MyPagination
    logging_methods = ('GET',)

    def get_queryset(self):
        menu = self.get_object()
        queryset = super().get_queryset().filter(menu=menu, parent__isnull=True)
        return queryset

    def get_object(self):
        try:
            obj = company_models.Menu.objects.get(id=self.kwargs.get(self.lookup_field))
            return obj
        except company_models.Menu.DoesNotExist:
            raise NotFound('menu does nit exist')


class MenuModifiersListView(LoggingMixin, generics.ListAPIView):
    """ Список modifier (вложенный список)"""
    queryset = product_models.Modifier.objects.all()
    serializer_class = dashboard_serializer.ModifierSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = MyPagination
    logging_methods = ('GET',)

    def get_queryset(self):
        menu = self.get_object()
        queryset = super().get_queryset().filter(menu=menu)
        return queryset

    def get_object(self):
        try:
            obj = company_models.Menu.objects.get(id=self.kwargs.get(self.lookup_field))
            return obj
        except company_models.Menu.DoesNotExist:
            raise NotFound('menu does not exist')


class ProductCategoryCreateView(LoggingMixin, generics.CreateAPIView):
    """ добавить категорию """
    queryset = product_models.ProductCategory.objects.all()
    serializer_class = dashboard_serializer.ProductCategoryCreateListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('POST',)


class ProductCreateView(LoggingMixin, generics.CreateAPIView):
    """ добавить продукт """
    queryset = product_models.ProductCategory.objects.all()
    serializer_class = dashboard_serializer.ProductCreateSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('POST',)


class ModifierCreateView(LoggingMixin, generics.CreateAPIView):
    """ добавить modifier """
    queryset = product_models.Modifier.objects.all()
    serializer_class = dashboard_serializer.ModifierSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('POST',)


class ModifierItemCreateView(LoggingMixin, generics.CreateAPIView):
    """ добавить modifier-item """
    queryset = product_models.ModifierItem.objects.all()
    serializer_class = dashboard_serializer.ModifierItemSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('POST',)


class ProductCategoryRetrieveUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ получить/обновит/обновить категорию """
    queryset = product_models.ProductCategory.objects.all()
    serializer_class = dashboard_serializer.ProductCategoryCreateListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    http_method_names = ('get', 'put', 'delete')
    logging_methods = ('GET', 'DELETE', 'PATCH', 'PUT')


class ProductRetrieveUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ получить/обновит/обновить продукт """
    queryset = product_models.ProductCategory.objects.all()
    serializer_class = dashboard_serializer.ProductCreateSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    http_method_names = ('get', 'put', 'delete')
    logging_methods = ('GET', 'DELETE', 'PATCH', 'PUT')


class ModifierRetrieveUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ получить/обновит/обновить modifier """
    queryset = product_models.Modifier.objects.all()
    serializer_class = dashboard_serializer.ModifierSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    http_method_names = ('get', 'put', 'delete')
    logging_methods = ('GET', 'DELETE', 'PATCH', 'PUT')


class ModifierItemRetrieveUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ получить/обновит/обновить modifier-item """
    queryset = product_models.ModifierItem.objects.all()
    serializer_class = dashboard_serializer.ModifierItemSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    http_method_names = ('get', 'put', 'delete')
    logging_methods = ('GET', 'DELETE', 'PUT')


class CompanyAllListView(LoggingMixin, generics.ListAPIView):
    """ Список всех компаний """
    queryset = company_models.Company.objects.all()
    serializer_class = dashboard_serializer.CompanySerializerForTakkOwnerSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = MyPagination
    logging_methods = ('GET',)


class CompanyRetrieveView(LoggingMixin, generics.ListAPIView):
    """ Список всех компаний """
    queryset = company_models.Company.objects.all()
    serializer_class = dashboard_serializer.CompanySerializerForTakkOwnerSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('GET',)


class UserProfileView(LoggingMixin, generics.RetrieveAPIView):
    """ Информация профиля
        User type:  COMPANY_OWNER = 1 EMPLOYEE = 2
    """
    queryset = user_models.User.objects.all()
    serializer_class = dashboard_serializer.UserProfileSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('GET',)

    def get_object(self):  # TODO изменить
        obj = self.get_queryset().get(phone='7777')
        return obj


class CompanyEmployeeView(LoggingMixin, generics.ListAPIView):
    """
    Список сорудников компании
    Manager = 1
    Cashier = 2
    """
    queryset = company_models.Employee.objects.all()
    serializer_class = dashboard_serializer.EmployeeSerializer
    pagination_class = MyPagination
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('GET', )


class CustomerListView(LoggingMixin, generics.ListAPIView):

    queryset = user_models.User.objects.all()
    serializer_class = dashboard_serializer.CustomerListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = MyPagination
    logging_methods = ('GET',)

    def get_queryset(self):  # TODO изменить
        queryset = super().get_queryset()
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['company'] = company_models.Company.objects.first()   # TODO изменить
        return context


class OrderTransactionView(LoggingMixin, generics.ListAPIView):
    """
    Транзакции заказов payment_type: ONLINE = 0 BALANCE = 1 CARD = 2 TERMINAL = 3 status:  PAID = 0 REFUND = 1 (это может еще изменится)
    """
    queryset = payment_models.OrderPaymentTransaction.objects.all()
    serializer_class = dashboard_serializer.OrderTransactionSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = MyPagination
    logging_methods = ('GET',)


class BudgetTransactionView(LoggingMixin, generics.ListAPIView):
    """ Транзакции пополнения баланса """
    queryset = payment_models.BudgetTransaction.objects.all()
    serializer_class = dashboard_serializer.BudgetTransactionSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = MyPagination
    logging_methods = ('GET',)

#
# class DuplicateMenuView(LoggingMixin, generics.GenericAPIView):
#     """ Создать дубликат меню для кафе"""
#     queryset = company_models.Cafe.objects.all()
#     serializer_class = ...
#