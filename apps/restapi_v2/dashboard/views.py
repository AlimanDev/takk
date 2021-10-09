from random import randint

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, serializers, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, APIException
from rest_framework_tracking.mixins import LoggingMixin

from django_filters import rest_framework as django_filters
from django.contrib.auth.hashers import check_password
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from apps.users import models as user_models
from apps.users import logics as user_logics
from apps.companies import models as company_models
from apps.orders import models as order_models
from apps.products import models as product_models
from apps.payment import models as payment_models
from apps.restapi_v2.dashboard import serializers as dashboard_serializers
from apps.restapi_v2.paginations import DashboardPagination
from apps.restapi_v2 import logics as restapi_v2_logics
from apps.restapi_v2.dashboard import logics as dashboard_logics


class LoginAPiView(LoggingMixin, generics.GenericAPIView):

    queryset = user_models.User.objects.all()
    serializer_class = dashboard_serializers.LoginSerializer
    permission_classes = (permissions.AllowAny, )
    http_method_names = ('post', )
    logging_methods = ('POST', )

    def post(self, request, *args, **kwargs):
        try:
            user: user_models.User
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid(raise_exception=False):
                raise APIException('Invalid data')
            phone = serializer.validated_data.get('phone')
            password = serializer.validated_data.get('password')
            user = restapi_v2_logics.get_user_phone(phone)
            if user.check_password(password):
                token = user_logics.get_tokens_for_user(user)
                return Response(token, status=status.HTTP_200_OK)
            else:
                raise APIException('Invalid password')
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(LoggingMixin, generics.RetrieveUpdateAPIView):
    """ Информация профиля
        User type:  COMPANY_OWNER = 1 EMPLOYEE = 2
    """
    queryset = user_models.User.objects.all()
    serializer_class = dashboard_serializers.UserProfileSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('GET',)

    def get_object(self):  # TODO изменить
        obj = self.get_queryset().get(phone='7777')
        return obj


class CompanyListAPIView(LoggingMixin, generics.ListAPIView):
    """ Список всех компаний """
    queryset = company_models.Company.objects.all()
    serializer_class = dashboard_serializers.CompanySerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = DashboardPagination
    logging_methods = ('GET',)

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = company_models.Company.objects.all()
        else:  # FIXME
            queryset = company_models.Company.objects.all()
        return queryset


class CompanyUpdateAPIView(LoggingMixin, generics.RetrieveUpdateAPIView):
    """Обновить компанию"""
    queryset = company_models.Company.objects.all()
    serializer_class = dashboard_serializers.CompanySerializer
    permission_classes = (permissions.AllowAny, )  # TODO изменить
    logging_methods = ('GET', 'PUT')

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = company_models.Company.objects.all()
        else:  # FIXME
            queryset = company_models.Company.objects.all()
        return queryset


class CafeUpdateAPIView(LoggingMixin, generics.ListAPIView):
    """  Список кафе компании
    status: BLOCKED = 0 ACTIVE = 1 PENDING = 2"""
    queryset = company_models.Cafe.objects.all()
    serializer_class = dashboard_serializers.CafeSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = DashboardPagination
    logging_methods = ('GET', 'PUT', 'DELETE')


class CompanyMenuListAPIView(LoggingMixin, generics.ListAPIView):
    queryset = company_models.Company.objects.all()
    serializer_class = dashboard_serializers.MenuListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = DashboardPagination
    logging_methods = ('GET',)

    def get_queryset(self):
        company = company_models.Company.objects.all().first()  # FIXME:
        if company:
            return company.company_menus.all()
        return list()


# class CustomerListAPIView(LoggingMixin, generics.ListAPIView):
#     queryset = user_models.User.objects.all()
#     serializer_class = dashboard_serializer.CustomerListSerializer
#     permission_classes = (permissions.AllowAny,)  # TODO изменить
#     pagination_class = MyPagination
#     logging_methods = ('GET',)
#
#     def get_queryset(self):  # TODO изменить
#         queryset = super().get_queryset()
#         return queryset
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['company'] = company_models.Company.objects.first()   # TODO изменить
#         return context


class CompanyUpdateDeleteAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = company_models.Company.objects.all()
    serializer_class = dashboard_serializers.MenuListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    http_method_names = ('put', 'delete')
    logging_methods = ('PUT', 'DELETE')

    def get_queryset(self):
        company = company_models.Company.objects.all().first()  # FIXME:
        if company:
            return company.company_menus.all()
        return list()

    def get_object(self):  # TODO: нужно изменить логику
        try:
            obj = self.get_queryset().get(pk=self.kwargs.get('menu_id'))
            return obj
        except Exception as e:
            raise NotFound("Menu does not exist")


class MenuProductsListView(LoggingMixin, generics.ListAPIView):
    """ Товары меню """
    queryset = product_models.Product.objects.all()
    serializer_class = dashboard_serializers.ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = DashboardPagination
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
    serializer_class = dashboard_serializers.ProductCategoryCreateListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = DashboardPagination
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
    serializer_class = dashboard_serializers.ModifierSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    pagination_class = DashboardPagination
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


class ModifierItemRetrieveUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ получить/обновит/обновить modifier-item """
    queryset = product_models.ModifierItem.objects.all()
    serializer_class = dashboard_serializers.ModifierItemSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    http_method_names = ('get', 'put', 'delete')
    logging_methods = ('GET', 'DELETE', 'PUT')


class ModifierItemCreateView(LoggingMixin, generics.CreateAPIView):
    """ добавить modifier-item """
    queryset = product_models.ModifierItem.objects.all()
    serializer_class = dashboard_serializers.ModifierItemSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('POST',)


class ModifierRetrieveUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ получить/обновит/обновить modifier """
    queryset = product_models.Modifier.objects.all()
    serializer_class = dashboard_serializers.ModifierSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    http_method_names = ('get', 'put', 'delete')
    logging_methods = ('GET', 'DELETE', 'PUT')


class ModifierCreateView(LoggingMixin, generics.CreateAPIView):
    """ добавить modifier """
    queryset = product_models.Modifier.objects.all()
    serializer_class = dashboard_serializers.ModifierSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('POST',)


class ProductCategoryRetrieveUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ получить/обновит/обновить категорию """
    queryset = product_models.ProductCategory.objects.all()
    serializer_class = dashboard_serializers.ProductCategoryCreateListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    http_method_names = ('get', 'put', 'delete')
    logging_methods = ('GET', 'DELETE', 'PUT')


class ProductCategoryCreateView(LoggingMixin, generics.CreateAPIView):
    """ добавить категорию """
    queryset = product_models.ProductCategory.objects.all()
    serializer_class = dashboard_serializers.ProductCategoryCreateListSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('POST',)


class ProductRetrieveUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ получить/обновит/обновить продукт """
    queryset = product_models.Product.objects.all()
    serializer_class = dashboard_serializers.ProductSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    http_method_names = ('get', 'put', 'delete')
    logging_methods = ('GET', 'DELETE', 'PUT')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return dashboard_serializers.ProductSerializer
        return dashboard_serializers.ProductCreateSerializer


class ProductCreateView(LoggingMixin, generics.CreateAPIView):
    """ добавить продукт """
    queryset = product_models.Product.objects.all()
    serializer_class = dashboard_serializers.ProductCreateSerializer
    permission_classes = (permissions.AllowAny,)  # TODO изменить
    logging_methods = ('POST',)


class SortedMenuProductsAPIView(LoggingMixin, generics.GenericAPIView):
    """ """
    serializer_class = dashboard_serializers.SortedSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ('post',)
    logging_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid(raise_exception=False):
                raise APIException('Invalid data')
            data = serializer.validated_data
            obj_type = data.get('obj_type')
            if obj_type == 'product':
                self._update_position(data.get('obj_list'), dashboard_logics.get_product)
            elif obj_type == 'modifier':
                self._update_position(data.get('obj_list'), dashboard_logics.get_modifier)
            elif obj_type == 'modifier_item':
                self._update_position(data.get('obj_list'), dashboard_logics.get_modifier_item)
            elif obj_type == 'product_category':
                self._update_position(data.get('obj_list'), dashboard_logics.get_product_category)
            else:
                raise APIException('Invalid object type')
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _update_position(data, func):
        if data:
            for item in data:
                try:
                    print(item)
                    obj = func(item.get('id'))
                    obj.position = item.get('position')
                    obj.save(update_fields=['position', ])
                except Exception as e:
                    continue



