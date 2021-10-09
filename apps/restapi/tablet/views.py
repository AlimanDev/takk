from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, permissions, serializers, status, viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_tracking.mixins import LoggingMixin

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.conf import settings
from django_filters import rest_framework as django_filters

from apps.users import models as user_models
from apps.restapi.tablet import serializers as tablet_serializers
from apps.companies import models as company_models
from apps.orders import models as order_models
from apps.payment import models as payment_models
from apps.products import models as product_models
from apps.restapi import pagination
from apps.users import logics as user_logics
from apps.restapi.mobile import client_views_logic as mobile_logics
from random import randint
import stripe
import json
import datetime


class ProductCategoryCheckView(LoggingMixin, generics.GenericAPIView):
    """ Проверить обновленные категории """
    serializer_class = tablet_serializers.ProductCategoryCheckSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ('post', )
    logging_methods = ('POST', )

    def post(self, request, *args, **kwargs):
        update_at = self.get_update_at()
        cafe = self.get_object()
        result = {}
        data = {}
        if cafe and (not request.data or request.data.get('update_at') == "" or request.data.get('update_at')):
            data['categories'] = self.get_queryset()
            result['status'] = 0
            result['message'] = 'Success'

        elif update_at and cafe:
            data['categories'] = self.get_queryset().filter(updated_dt__gte=update_at)
            result['status'] = 0
            result['message'] = 'Success'
        else:
            data['categories'] = []
            result['status'] = 1
            result['message'] = 'error'

        data['server_time'] = self.get_server_time()
        result['data'] = data
        return Response(data=tablet_serializers.ProductCategoryCheckSerializer(
            result, context={'request': request}).data, status=status.HTTP_200_OK)

    def get_update_at(self):
        serializer = tablet_serializers.ProductCategoryCheckSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=False):
            return serializer.validated_data['update_at']
        else:
            return None

    @staticmethod
    def get_server_time():
        return datetime.datetime.now()

    def get_queryset(self):
        cafe = self.get_object()
        queryset = cafe.menu.categories.filter(parent__isnull=True)
        return queryset

    def get_object(self):
        try:
            obj = company_models.Cafe.objects.get(pk=self.kwargs.get(self.lookup_field))
        except company_models.Cafe.DoesNotExist:
            obj = None
        return obj


class ProductSubCategoryCheckView(LoggingMixin, generics.GenericAPIView):
    """ Проверить обновленные суб-категорий """
    serializer_class = tablet_serializers.ProductSubCategoryCheckSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ('post', )
    logging_methods = ('POST', )

    def post(self, request, *args, **kwargs):
        update_at = self.get_update_at()
        cafe = self.get_object()
        result = {}
        data = {}

        if cafe and (not request.data or request.data.get('update_at') == "" or request.data.get('update_at')):
            data['sub_categories'] = self.get_queryset()
            result['status'] = 0
            result['message'] = 'Success'

        elif update_at and cafe:
            data['sub_categories'] = self.get_queryset().filter(updated_dt__gte=update_at)
            result['status'] = 0
            result['message'] = 'Success'
        else:
            data['sub_categories'] = []
            result['status'] = 1
            result['message'] = 'error'

        data['server_time'] = self.get_server_time()
        result['data'] = data
        return Response(data=tablet_serializers.ProductSubCategoryCheckSerializer(
            result, context={'request': request}).data, status=status.HTTP_200_OK)

    def get_update_at(self):
        serializer = tablet_serializers.ProductSubCategoryCheckSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=False):
            return serializer.validated_data['update_at']
        else:
            return None

    @staticmethod
    def get_server_time():
        return datetime.datetime.now()

    def get_queryset(self):
        cafe = self.get_object()
        queryset = cafe.menu.categories.filter(parent__isnull=False)
        return queryset

    def get_object(self):
        try:
            obj = company_models.Cafe.objects.get(pk=self.kwargs.get(self.lookup_field))
        except company_models.Cafe.DoesNotExist:
            obj = None
        return obj


class ProductCheckView(LoggingMixin, generics.GenericAPIView):
    """ Проверить обновленные продуктов """

    serializer_class = tablet_serializers.ProductCheckSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post', ]
    logging_methods = ['POST', ]

    def post(self, request, *args, **kwargs):
        update_at = self.get_update_at()
        cafe = self.get_object()
        result = {}
        data = {}

        if cafe and (not request.data or request.data.get('update_at') == "" or request.data.get('update_at')):
            data['products'] = self.get_queryset()
            result['status'] = 0
            result['message'] = 'Success'

        elif update_at and cafe:
            data['products'] = self.get_queryset().filter(updated_dt__gte=update_at)
            result['status'] = 0
            result['message'] = 'Success'
        else:
            data['products'] = []
            result['status'] = 1
            result['message'] = 'error'

        data['server_time'] = self.get_server_time()
        result['data'] = data
        return Response(data=tablet_serializers.ProductCheckSerializer(
            result, context={'request': request}).data, status=status.HTTP_200_OK)

    def get_update_at(self):
        serializer = tablet_serializers.ProductCheckSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=False):
            return serializer.validated_data['update_at']
        else:
            return None

    @staticmethod
    def get_server_time():
        return datetime.datetime.now()

    def get_queryset(self):
        cafe = self.get_object()
        queryset = product_models.Product.objects.filter(category__menu=cafe.menu)
        return queryset

    def get_object(self):
        try:
            obj = company_models.Cafe.objects.get(pk=self.kwargs.get(self.lookup_field))
        except company_models.Cafe.DoesNotExist:
            obj = None
        return obj


class ProductSizeCheckView(LoggingMixin, generics.GenericAPIView):
    """ Проверить обновленные размеры товара """

    serializer_class = tablet_serializers.ProductSizeCheckSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post', ]
    logging_methods = ['POST', ]

    def post(self, request, *args, **kwargs):
        update_at = self.get_update_at()
        cafe = self.get_object()
        result = {}
        data = {}

        if cafe and (not request.data or request.data.get('update_at') == "" or request.data.get('update_at')):
            data['sizes'] = self.get_queryset()
            result['status'] = 0
            result['message'] = 'Success'

        elif update_at and cafe:
            data['sizes'] = self.get_queryset().filter(updated_dt__gte=update_at)
            result['status'] = 0
            result['message'] = 'Success'
        else:
            data['sizes'] = []
            result['status'] = 1
            result['message'] = 'error'

        data['server_time'] = self.get_server_time()
        result['data'] = data
        return Response(data=tablet_serializers.ProductSizeCheckSerializer(
            result, context={'request': request}).data, status=status.HTTP_200_OK)

    def get_update_at(self):
        serializer = tablet_serializers.ProductSizeCheckSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=False):
            return serializer.validated_data['update_at']
        else:
            return None

    @staticmethod
    def get_server_time():
        return datetime.datetime.now()

    def get_queryset(self):
        cafe = self.get_object()
        if cafe:
            queryset = product_models.ProductSize.objects.filter(product__category__menu=cafe.menu)
            return queryset
        return list()

    def get_object(self):
        try:
            obj = company_models.Cafe.objects.get(pk=self.kwargs.get(self.lookup_field))
        except company_models.Cafe.DoesNotExist:
            obj = None
        return obj


class ProductModifierCheckView(LoggingMixin, generics.GenericAPIView):
    """ Проверить обновленные категории модификаторов товара """

    serializer_class = tablet_serializers.ProductModifierCheckSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post', ]
    logging_methods = ['POST', ]

    def post(self, request, *args, **kwargs):
        update_at = self.get_update_at()
        cafe = self.get_object()
        result = {}
        data = {}

        if cafe and (not request.data or request.data.get('update_at') == "" or request.data.get('update_at')):
            data['modifiers'] = self.get_queryset()
            result['status'] = 0
            result['message'] = 'Success'

        elif update_at and cafe:
            data['modifiers'] = self.get_queryset().filter(updated_dt__gte=update_at)
            result['status'] = 0
            result['message'] = 'Success'
        else:
            data['modifiers'] = []
            result['status'] = 1
            result['message'] = 'error'

        data['server_time'] = self.get_server_time()
        result['data'] = data
        return Response(data=tablet_serializers.ProductModifierCheckSerializer(
            result, context={'request': request}).data, status=status.HTTP_200_OK)

    def get_update_at(self):
        serializer = tablet_serializers.ProductModifierCheckSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=False):
            return serializer.validated_data['update_at']
        else:
            return None

    @staticmethod
    def get_server_time():
        return datetime.datetime.now()

    def get_queryset(self):
        cafe = self.get_object()
        queryset = product_models.Modifier.objects.filter(menu=cafe.menu)
        return queryset

    def get_object(self):
        try:
            obj = company_models.Cafe.objects.get(pk=self.kwargs.get(self.lookup_field))
        except company_models.Cafe.DoesNotExist:
            obj = None
        return obj


class ProductModifierItemCheckView(LoggingMixin, generics.GenericAPIView):
    """ Проверить обновленные модификаторы товара """

    serializer_class = tablet_serializers.ProductModifierItemCheckSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post', ]
    logging_methods = ['POST', ]

    def post(self, request, *args, **kwargs):
        update_at = self.get_update_at()
        cafe = self.get_object()
        result = {}
        data = {}

        if cafe and (not request.data or request.data.get('update_at') == "" or request.data.get('update_at')):
            data['modifier_items'] = self.get_queryset()
            result['status'] = 0
            result['message'] = 'Success'

        elif update_at and cafe:
            data['modifier_items'] = self.get_queryset().filter(updated_dt__gte=update_at)
            result['status'] = 0
            result['message'] = 'Success'
        else:
            data['modifier_items'] = []
            result['status'] = 1
            result['message'] = 'error'

        data['server_time'] = self.get_server_time()
        result['data'] = data
        return Response(data=tablet_serializers.ProductModifierItemCheckSerializer(
            result, context={'request': request}).data, status=status.HTTP_200_OK)

    def get_update_at(self):
        serializer = tablet_serializers.ProductModifierItemCheckSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=False):
            return serializer.validated_data['update_at']
        else:
            return None

    @staticmethod
    def get_server_time():
        return datetime.datetime.now()

    def get_queryset(self):
        cafe = self.get_object()
        queryset = product_models.ModifierItem.objects.filter(modifier__menu=cafe.menu)
        return queryset

    def get_object(self):
        try:
            obj = company_models.Cafe.objects.get(pk=self.kwargs.get(self.lookup_field))
        except company_models.Cafe.DoesNotExist:
            obj = None
        return obj


class OrderCreateView(LoggingMixin, generics.GenericAPIView):
    """ Создать заказ
    если status = 0 заказ успешно создан
    если status = 1 неправильно заполнены данные
    если status = 2 ошибка при сохранении заказа
    """

    queryset = order_models.Order
    serializer_class = tablet_serializers.OrderSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post', ]
    logging_methods = ['POST', ]

    def post(self, request, *args, **kwargs):
        response_data = {}
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid(raise_exception=False):
            response_data['message'] = 'error'
            response_data['status'] = 1
            response_data['data'] = []
            response_status = status.HTTP_400_BAD_REQUEST
            return Response(data=response_data, status=response_status)
        try:
            serializer.save()
            response_data['message'] = 'Success'
            response_data['status'] = 2
            response_data['data'] = serializer.data
            response_status = status.HTTP_201_CREATED

        except Exception as e:
            response_data['message'] = str(e)
            response_data['status'] = 2
            response_data['data'] = []
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(data=response_data, status=response_status)


class CreateLocationForTerminalView(LoggingMixin, generics.GenericAPIView):
    """ Получить локацию """
    permission_classes = [permissions.AllowAny]  # TODO: разрешить только для авторизованных пользователей
    http_method_names = ('get', )
    logging_methods = ('get', )

    def get(self, request, *args, **kwargs):
        response_data = {}
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            location = stripe.terminal.Location.create(
                display_name='HQ',
                address={  # TODO: нужно решить откуда будем брать эти данные
                    'line1': '1272 Valencia Street',
                    'city': 'San Francisco',
                    'state': 'CA',
                    'country': 'US',
                    'postal_code': '94110',
                },
            )
            response_data['message'] = 'Success'
            response_data['status'] = 0
            response_data['location'] = location
        except Exception as e:
            response_data['message'] = str(e)
            response_data['status'] = 1
            response_data['location'] = str()

        return Response(data=response_data, status=status.HTTP_200_OK)


class CreateTokenForTerminalView(LoggingMixin, generics.CreateAPIView):
    """ Получить токен """

    permission_classes = [permissions.AllowAny]  # TODO: разрешить только для авторизованных пользователей
    http_method_names = ('get',)
    logging_methods = ('GET',)

    def get(self, request, *args, **kwargs):
        response_data = {}
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            connection_token = stripe.terminal.ConnectionToken.create()
            response_data['message'] = 'Success'
            response_data['status'] = 0
            response_data['connect_token'] = connection_token.secret
        except Exception as e:
            response_data['message'] = str(e)
            response_data['status'] = 1
            response_data['connect_token'] = str()

        return Response(data=response_data, status=status.HTTP_200_OK)


class OrderPaymentView(LoggingMixin, generics.GenericAPIView):  # TODO для теста
    """ Получить client_secret для оплаты заказа """
    queryset = order_models.Order.objects.all()
    permission_classes = [permissions.AllowAny]  # TODO: разрешить только для авторизованных пользователей
    http_method_names = ('get', )
    logging_methods = ('GET', )

    def get(self, request, *args, **kwargs):
        response_data = {}
        try:
            order = self.get_object()
            stripe.api_key = settings.STRIPE_SECRET_KEY
            payment_intent = stripe.PaymentIntent.create(
                amount=order.get_total_price_in_cents(),
                currency='usd',
                payment_method_types=['card_present'],
                capture_method='manual',
                metadata={
                    'type': 'terminal',
                    'order_id': order.id
                })
            response_data['message'] = 'Success'
            response_data['status'] = 0
            response_data['client_secret'] = payment_intent.client_secret
        except Exception as e:
            response_data['message'] = str(e)
            response_data['status'] = 1
            response_data['client_secret'] = str()

        return Response(data=response_data, status=status.HTTP_200_OK)


class FinishOrderPaymentView(LoggingMixin, generics.GenericAPIView):  # TODO для теста
    """ Завершить оплату заказа """
    queryset = order_models.Order.objects.all()
    serializer_class = tablet_serializers.FinishOrderPaymentSerializer
    permission_classes = [permissions.AllowAny]  # TODO: разрешить только для авторизованных пользователей
    http_method_names = ('post', )
    logging_methods = ('POST', )

    def post(self, request, *args, **kwargs):
        response_data = {}
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            stripe.api_key = settings.STRIPE_SECRET_KEY
            payment_intent = stripe.PaymentIntent.capture(
                serializer.validated_data.get('payment_id'))
            order_id = payment_intent.metadata.get('order_id')
            self._create_transaction(order_id, payment_intent.id)

            response_data['message'] = 'Success'
            response_data['status'] = 0

        except Exception as e:
            response_data['message'] = str(e)
            response_data['status'] = 1

        return Response(data=response_data, status=status.HTTP_200_OK)

    @staticmethod  # TODO: возможно эту фукцию придется перенести в celery_task
    def _create_transaction(order_id: int, payment_intent_id: str):
        transaction = payment_models.OrderPaymentTransaction()
        order = mobile_logics.get_order(order_id)
        transaction.user = order.user
        transaction.order = order
        transaction.cafe = order.cafe
        transaction.payment_id = payment_intent_id
        transaction.amount = order.get_total_price_in_cents()
        transaction.payment_type = payment_models.OrderPaymentTransaction.TERMINAL
        transaction.takk_fee = mobile_logics.get_takk_fee(order)
        transaction.save()
        mobile_logics.order_paid(order)  # изменяет статус заказа на paid



