import pdb

import stripe
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django_filters import rest_framework as filters
from django.contrib.auth.hashers import check_password

from apps.users import models as user_models
from apps.restapi.mobile import serializers as mobile_serializers
from apps.companies import models as company_models
from apps.orders import models as order_models
from apps.products import models as product_models
from random import randint
from apps.restapi import pagination
from apps.restapi import permissions as restapi_permissions
from apps.restapi.mobile import send_notifications
from apps.restapi.exceptions import CustomException
from apps.payment import models as payment_models
from apps.payment.logic import refund as refund_logics
from django.conf import settings
from rest_framework_tracking.mixins import LoggingMixin
from django.db.models import Q
from drf_yasg import openapi
from apps.restapi import tasks as restapi_tasks
from apps.restapi.mobile import client_views_logic as view_logics


class EmployeeCafesListView(LoggingMixin, generics.ListAPIView):
    """ Список доступных сотруднику кафе  """
    serializer_class = mobile_serializers.CafeSerializer
    permission_classes = [permissions.IsAuthenticated & restapi_permissions.IsEmployee]
    pagination_class = pagination.MyPagination
    logging_methods = ['GET', ]

    def get_queryset(self):
        queryset = self.request.user.employee.cafes.all()
        return queryset


class EmployeeCafeOrdersView(LoggingMixin, generics.ListAPIView):
    """ Список заказов кафе. state: ['waiting', 'new', 'ready', 'refund', sent_out', 'delivered']  """
    queryset = order_models.Order.objects.all()
    serializer_class = mobile_serializers.OrderForEmployeeSerializer
    permission_classes = [permissions.IsAuthenticated & restapi_permissions.IsEmployee, ]
    pagination_class = pagination.MyPagination
    logging_methods = ['GET', ]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('state', openapi.IN_QUERY, description="state", type=openapi.TYPE_STRING),
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset.filter(cafe__in=self.request.user.employee.cafes.all())
        if self.request.query_params.get('state', False):
            queryset = queryset.filter(status=self.request.query_params.get('state'))
        if self.request.query_params.get('state') == order_models.Order.NEW:
            queryset = queryset.order_by('pre_order_timestamp')
        return queryset


class EmployeeUpdateOrderStatusView(LoggingMixin, generics.UpdateAPIView):
    """ Изменить статус заказа """
    queryset = order_models.Order.objects.all()
    permission_classes = [permissions.IsAuthenticated & restapi_permissions.IsEmployee]
    serializer_class = mobile_serializers.OrderUpdateStatusSerializer
    http_method_names = ['put', ]
    logging_methods = ['PUT', ]


class EmployeeProductStatusUpdateView(LoggingMixin, generics.UpdateAPIView):
    """ Изменить статус товара available"""
    queryset = product_models.Product.objects.all()
    serializer_class = mobile_serializers.EmployeeProductStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated & restapi_permissions.IsEmployee]
    http_method_names = ['put', ]
    logging_methods = ['PUT', ]


class RefundPaymentOrderView(LoggingMixin, generics.GenericAPIView):
    """ Возврат средств
        Нужно указать только один клич из order_refund, amount или items
        order_refund возвращяет клиенту всю сумму заказа
        amount возвращяет клиенту определённую сумму amount (amount не может быть больше order_total_price)
        items возвращяет сумму указанных товаров
        Ответы:
        если успешно {'refund_amount': XXXX} status 200
        если ошибка {'detail': (error)} status 400
    """
    queryset = order_models.Order.objects.all()
    serializer_class = mobile_serializers.RefundPaymentOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', ]
    logging_methods = ['POST', ]

    def post(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            serializer = mobile_serializers.RefundPaymentOrderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)  # TODO Добавить валидацию
            data = serializer.validated_data
            transaction = refund_logics.get_transaction(order)
            if self.check_transaction_status(transaction):  # Проверяет статус чтобы не было дублирования возврата
                return Response({'detail': 'this order was refunded'}, status=status.HTTP_400_BAD_REQUEST)
            return self.refund(transaction, order, self.request.user, data)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def check_transaction_status(transaction):
        if transaction.status == payment_models.OrderPaymentTransaction.REFUND:
            return True
        return False

    @staticmethod
    def refund(transaction, order, employee, data):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            refund_data = refund_logics.get_refund_data(  # вернет данные для возврата средств
                transaction, employee, order, data)
            if transaction.payment_type == payment_models.OrderPaymentTransaction.BALANCE:  # если заказ был оплачен с баланса
                refund_logics.save_refund_balance_payment(refund_data)  # сохраняет возврат
                refund_logics.refund_amount_to_user_balance(refund_data)  # (вернет деньги на баланс клиента)
                refund_logics.make_order_status_refund(refund_data.get('order'))  # изменит статус заказа на REFUND
                return Response({'refund_amount': refund_data.get('refund_amount')}, status=status.HTTP_200_OK)
            elif transaction.payment_type == payment_models.OrderPaymentTransaction.ONLINE:  # если заказ был оплачен онлайн

                if transaction.is_capture:  # если средства уже захвачены (переведены на баланс Stripe)
                    try:

                        refund = stripe.Refund.create(  # Возврат средст из счета Stripe на карту клиента
                            payment_intent=transaction.payment_id,
                            amount=int(refund_data.get('refund_amount') * 100)
                        )
                    except Exception as e:
                        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    refund_logics.make_order_status_refund(refund_data.get('order'))  # order.status == Refund
                    refund_logics.save_refund_online_payment(  # сохраняет Refund
                        refund_data, refund.id)
                    return Response({'refund_amount': refund_data.get('refund_amount')}, status=status.HTTP_200_OK)
                else:  # если средсва еще не были захвачены (перевод на баланс Stripe еще не был)
                    try:
                        # сумму на счет страйп (order_amount - refund_amount)
                        capture_amount = transaction.amount - int(refund_data.get('refund_amount') * 100)
                        print(capture_amount)
                        if data.get('order_refund') or capture_amount == 0:
                            cancel = stripe.PaymentIntent.cancel(
                                transaction.payment_id
                            )
                        else:
                            capture = stripe.PaymentIntent.capture(
                                transaction.payment_id,
                                amount_to_capture=capture_amount
                            )

                    except Exception as e:
                        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    refund_logics.make_order_status_refund(refund_data.get('order'))
                    refund_logics.save_refund_online_payment(refund_data)
                    return Response({'refund_amount': refund_data.get('refund_amount')}, status=status.HTTP_200_OK)
            else:  # transaction status = Card
                if transaction.is_capture:
                    final_transaction = transaction.final_transaction
                    try:
                        refund = stripe.Refund.create(
                            payment_intent=final_transaction.payment_id,
                            amount=int(refund_data.get('refund_amount') * 100)
                        )
                    except Exception as e:
                        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    refund_logics.make_order_status_refund(refund_data.get('order'))
                    refund_logics.save_refund_online_payment(refund_data, refund.id)
                    return Response({'refund_amount': refund_data.get('refund_amount')}, status=status.HTTP_200_OK)
                else:
                    try:
                        capture = stripe.PaymentIntent.capture(
                            transaction.payment_id,
                            amount_to_capture=(transaction.amount - int(refund_data.get('refund_amount') * 100))
                        )

                    except Exception as e:
                        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    refund_logics.make_order_status_refund(refund_data.get('order'))
                    refund_logics.save_refund_online_payment(refund_data)
                    return Response({'refund_amount': refund_data.get('refund_amount')}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReadyKitchenOrderItemView(LoggingMixin, generics.GenericAPIView):
    """ Готовые заказы с кухни """
    queryset = order_models.OrderItem.objects.all()
    serializer_class = mobile_serializers.ReadyOrderItemSerializer
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee, )
    http_method_names = ('post', )
    logging_methods = ('POST', )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        view_logics.order_item_ready(serializer.validated_data.get('order_items'))
        return Response(status=status.HTTP_200_OK)


class ReadyMainOrderItemView(LoggingMixin, generics.GenericAPIView):
    """ Готовые заказы с кафе """
    queryset = order_models.OrderItem.objects.all()
    serializer_class = mobile_serializers.ReadyOrderItemSerializer
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee,)
    http_method_names = ('post',)
    logging_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        view_logics.order_item_ready(serializer.validated_data.get('order_items'))
        return Response(status=status.HTTP_200_OK)


class EmployeeCafeOrderDetailView(LoggingMixin, generics.RetrieveAPIView):
    """ Посмотреть заказ """
    queryset = order_models.Order.objects.all()
    serializer_class = mobile_serializers.OrderForEmployeeSerializer
    permission_classes = [permissions.IsAuthenticated & restapi_permissions.IsEmployee]
    http_method_names = ('get', )
    logging_methods = ('GET', )

    def get_queryset(self):
        return super().get_queryset().filter(cafe__in=self.request.user.employee.cafes.all())


# class RefundNew(LoggingMixin, generics.GenericAPIView):
#     queryset = order_models.Order.objects.all()
#     serializer_class = mobile_serializers.RefundPaymentOrderSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     http_method_names = ['post', ]
#     logging_methods = ['POST', ]

class OrderAcknowledgeView(LoggingMixin, generics.GenericAPIView):
    """ Order acknowledge (сотрудник принял заказ is_acknowledge = True)"""
    queryset = order_models.Order.objects.all()
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee,)
    http_method_names = ('get',)
    logging_methods = ('GET',)

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if not order.is_acknowledge:
            order.is_acknowledge = True
            order.save(update_fields=['is_acknowledge', ])
            send_notifications.user_order_acknowledge(order)
        return Response(status=status.HTTP_200_OK)


class EmployeeGivePointToCustomerView(LoggingMixin, generics.GenericAPIView):
    """ Дать point клиенту """
    queryset = user_models.User.objects.all()
    serializer_class = mobile_serializers.EmployeeGivePointSerializer
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee,)
    http_method_names = ('post',)
    logging_methods = ('post',)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                raise CustomException('Invalid data')
            data = serializer.validated_data
            user = self._get_user(data.get('phone', ''))
            company = view_logics.get_company(data.get('company'))
            self._give_point_to_user(user, company, data.get('points'))
            restapi_tasks.send_notification.delay(user.id, title='test', body='test')
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            raise CustomException(str(e))

    @staticmethod
    def _get_user(phone: str) -> user_models.User:
        try:
            user = user_models.User.objects.get(phone=phone)
            return user
        except user_models.User.DoesNotExist:
            raise CustomException('Does not exist user')

    @staticmethod
    def _give_point_to_user(user: user_models.User,
                            company: company_models.Company, points: int):
        user_points = user.get_company_points(company)
        sum_points = points + user_points.points
        free_items_count = int(sum_points / company.exchangeable_point)
        points = sum_points - free_items_count * company.exchangeable_point
        user_points.points = points
        user_points.save(update_fields=['points', ])
        view_logics.save_user_free_item(user, company, free_items_count)

