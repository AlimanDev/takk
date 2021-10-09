import datetime
from typing import Optional, Union
# LIBS
import stripe
from django.db.models import QuerySet, Prefetch
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework_tracking.mixins import LoggingMixin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError, APIException

# DJANGO
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.conf import settings
from django.utils.decorators import method_decorator

# APPS
from apps.restapi_v2 import serializers as restapi_v2_serializers
from apps.restapi_v2 import logics as restapi_v2_logics
from apps.restapi_v2 import tasks as restapi_v2_tasks
from apps.restapi_v2.mobile import serializers as mobile_serializers
from apps.restapi_v2.mobile import logics as mobile_logics
from apps.restapi_v2.paginations import MobilePagination

from apps.users import models as user_models
from apps.payment.logic import balance as balance_payment_logics
from apps.payment.logic import logics as payment_logics
from apps.payment import models as payment_models
from apps.companies import models as company_models
from apps.orders import models as order_models
from apps.restapi_v2 import permissions as restapi_permissions
from apps.products import models as product_models
from apps.payment.logic import charge as card_logics

class UserAuthAPIView(LoggingMixin, generics.GenericAPIView):
    """
    Регистраци и авторизация
    Если отправить только номер телефона то на номер отправляется смс код
    Если отправить смс код и номер телефона то вернет токен
    Если ключ register содержит False, надо предложить заполнить поля,
    как минимум username (API для редактирование юзера)
    """
    serializer_class = mobile_serializers.UserAuthSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ('post',)
    logging_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response({'detail': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        user, created = user_models.User.objects.get_or_create(phone=data.get('phone'))
        if created:  # Если пользователь был создан отправляется смс код на номер
            restapi_v2_logics.user_send_sms_code(user)
            return Response(data={"detail": "User created"}, status=status.HTTP_201_CREATED)
        else:
            if data.get('sms_code'):
                if int(data.get('sms_code')) == user.sms_code:
                    self.change_sms_code(user)
                    response_data = restapi_v2_logics.get_tokens_for_user(user)  # вернёт dict с токенами
                    response_data['register'] = True
                    if not user.username:  # если пользователь нет минимальных данных (предложить их заполнить)
                        response_data['register'] = False
                    return Response(data=response_data, status=status.HTTP_200_OK)
                else:
                    return Response(data={"detail": "Invalid code"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                restapi_v2_logics.user_send_sms_code(user)
                return Response(data={"detail": "SMS was sent to you"}, status=status.HTTP_200_OK)

    @staticmethod
    def change_sms_code(user: user_models.User):
        user.sms_code = 123456  # TODO: не забудь изменить его
        user.save(update_fields=['sms_code', ])


class UserProfileAPIView(LoggingMixin, generics.RetrieveUpdateAPIView):
    """ GET/PUT пользователя
        user_type = 1 владелец компании (owner)
        user_type = 2 сотрудник компании (employee)
        user_type = 3 обычный пользователь (user)
    """
    serializer_class = mobile_serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get', 'put')
    logging_methods = ('GET', 'PUT')

    def get_object(self):
        return self.request.user


class UserPointAPIView(LoggingMixin, generics.ListAPIView):
    """User points"""
    serializer_class = mobile_serializers.UserPointSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MobilePagination
    logging_methods = ('GET',)

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = user_models.Point.objects.select_related('company').filter(user_id=user_id)
        return queryset


class UserNotificationAPIView(LoggingMixin, generics.ListAPIView):
    """ Уведомления пользователя """
    queryset = user_models.UserNotification.objects.all()
    serializer_class = mobile_serializers.UserNotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MobilePagination
    logging_methods = ('GET',)

    def get_queryset(self):
        return self.request.user.notifications.all()


class UserBalanceFillHistoryAPIView(LoggingMixin, generics.ListAPIView):
    """ История пополнений баланса пользователя """
    queryset = user_models.BudgetFillHistory.objects.all()
    serializer_class = mobile_serializers.UserFillHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MobilePagination
    logging_methods = ('GET',)

    def get_queryset(self):
        return self.request.user.fill_histories.all()


class UserFreeItemsAPIView(LoggingMixin, generics.ListAPIView):
    """ Список всех FreeItems пользователя """
    serializer_class = mobile_serializers.UserFreeItemsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MobilePagination
    logging_methods = ('GET',)

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = user_models.FreeItem.objects.select_related('company').select_related('product').filter(
            user_id=user_id)
        return queryset


class UserCardListAPIView(LoggingMixin, generics.ListAPIView):
    """ Список карт пользователя """
    serializer_class = mobile_serializers.UserCardSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MobilePagination
    logging_methods = ('GET',)

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = payment_models.CustomerCard.objects.filter(user_id=user_id)
        return queryset


class UserSaveCardAPIView(LoggingMixin, generics.GenericAPIView):
    """
        Сохранить карту
        вернет client_secret статус 200
        если ошибка detail': error статус 400
    """
    serializer_class = mobile_serializers.UserCardCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('POST',)
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            user = self.request.user
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid(raise_exception=False):
                raise ValidationError(detail='Card name invalid')
            customer, created = payment_models.StripeCustomer.objects.get_or_create(user=user)
            if created:
                stripe_customer = stripe.Customer.create(
                    phone=user.phone
                )  # создает в страйпе customer
                customer.customer_id = stripe_customer.id
                customer.save(update_fields=['customer_id', ])
                customer.customer_id = stripe_customer.id  # сохраняет stripe_customer_id

            setup_intent = stripe.SetupIntent.create(
                customer=customer.customer_id,
                usage='off_session',  # чтобы мы могли снимать деньги любое время не спрашивая у пользователя
                metadata={
                    'user_id': user.id,
                    'card_name': serializer.validated_data.get('card_name')
                }
            )
            return Response({'client_secret': setup_intent.client_secret}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserCardUpdateDeleteAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ Узменить имя карты / удалить карту """
    queryset = payment_models.CustomerCard.objects.all()
    serializer_class = mobile_serializers.UserCardCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('put', 'delete')
    logging_methods = ('PUT', 'DELETE')

    def perform_destroy(self, instance):
        charges = self._get_charges_card(instance)  # если есть замароженные транзакции
        if charges:
            for charge in charges:
                self._capture_charge(charge)  # захват средств
        self._delete_card_in_stripe(instance.card_id)  # удалит карту из страйпа
        instance.delete()

    @staticmethod
    def _get_charges_card(card: payment_models.CustomerCard):  # замароженные транзакции
        charges = payment_models.OrderPaymentTransaction.objects.filter(
            card=card, is_capture=False)
        return charges

    @staticmethod
    def _capture_charge(transaction: payment_models.OrderPaymentTransaction):  # захват средств
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            payment_intent = stripe.PaymentIntent.capture(transaction.payment_id)
            if payment_intent.status == 'succeeded':
                transaction.is_capture = True
                transaction.save(update_fields=['is_capture', ])
            else:
                raise ValidationError('error mobile view 223')  # FIXME
        except Exception as e:
            raise ValidationError(str(e))

    @staticmethod
    def _delete_card_in_stripe(card_id: str):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            pm = stripe.PaymentMethod.detach(card_id)
            print(str(pm))
        except Exception as e:
            raise ValidationError(str(e))


class UserTopUpBalanceAPIView(LoggingMixin, generics.GenericAPIView):
    """
    payment_type = 0 оплата тарифа онлайн вернет {"client_secret" : "xxxxxxxxxxx"}  cтатусом 201
    payment_type = 1 оплата тарифа c карты вернет  {"detail": "paid"}  статусом 201
    если payment_type = 1 то card_id (required)
    """
    queryset = user_models.BudgetTariff.objects.all()
    serializer_class = mobile_serializers.TopUpBalanceSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('post',)
    logging_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid(raise_exception=False):
                raise ValidationError('Invalid data')
            tariff = self.get_object()
            user = self.request.user
            payment_type = serializer.validated_data.get('payment_type')
            response_data = dict()
            if payment_type == 0:  # Онлайн оплата
                response_data = balance_payment_logics.top_up_balance_online(user, tariff)
            elif payment_type == 1 and serializer.validated_data.get('card_id'):  # Оплата с карты
                card_id = serializer.validated_data.get('card_id')
                response_data = balance_payment_logics.top_up_balance_with_card(user, tariff, card_id)
            else:
                raise ValidationError('Invalid payment type or invalid payment card')
            return Response(data=response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        try:
            tariff = user_models.BudgetTariff.objects.get(pk=self.request.data.get('tariff_id'))
            return tariff
        except user_models.BudgetTariff.DoesNotExist:
            raise NotFound('Tariff does not exist')


class UserFavoriteCafeAPIView(LoggingMixin, generics.GenericAPIView):
    """
        Избранные кафе пользователя добавить/удалить
        если поле is_favorite = True добавляет
        если поле is_favorite = False удаляет
    """
    queryset = company_models.Cafe.objects.all()
    serializer_class = mobile_serializers.UserCafeFavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('post',)
    logging_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        user = request.user
        cafe = self.get_object()
        is_favorite = request.data.get('is_favorite')
        if is_favorite:
            user.favorite_cafes.add(cafe)
        else:
            user.favorite_cafes.remove(cafe)
        return Response(status=status.HTTP_200_OK)


class CompanyListAPIView(LoggingMixin, generics.ListAPIView):
    """ Список компаний """
    queryset = company_models.Company.objects.all()
    serializer_class = restapi_v2_serializers.CompanySerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = MobilePagination
    logging_methods = ('GET',)


class CompanyRetrieveAPIView(LoggingMixin, generics.RetrieveAPIView):
    """ Компания """
    queryset = company_models.Company.objects.all()  # TODO: возможно нужно добавить список кафе этой компании
    serializer_class = restapi_v2_serializers.CompanySerializer
    permission_classes = (permissions.AllowAny,)
    logging_methods = ('GET',)


class TariffListView(LoggingMixin, generics.ListAPIView):
    """ Список тарифов для пополнения баланса (BUDGET)"""
    queryset = user_models.BudgetTariff.objects.all()
    serializer_class = restapi_v2_serializers.TariffSerializer
    permission_classes = (permissions.AllowAny,)
    logging_methods = ('GET',)


class CafeListAPIView(LoggingMixin, generics.ListAPIView):
    """ Список кафе
        Также можно сделать поиск по названии кафе, описании кафе и по названии компании (на всякий случай)
        Если передать в параметры местоположение вернет список кафе сортированный по дистанции от местоположения
    """
    queryset = company_models.Cafe.objects.select_related('company').prefetch_related('week_time').filter(  # фильтрация статус активный, компания статус активный
        status=company_models.Cafe.ACTIVE, company__is_activate=True)
    serializer_class = mobile_serializers.CafeListSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('company__name', 'description', 'name')
    pagination_class = MobilePagination
    logging_methods = ('GET',)

    @swagger_auto_schema(manual_parameters=[  # для генерации схемы (swagger)
        openapi.Parameter('lat', openapi.IN_QUERY, description="latitude", type=openapi.TYPE_STRING),
        openapi.Parameter('long', openapi.IN_QUERY, description="longitude", type=openapi.TYPE_STRING),

    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        # Фильтрация по гео данным
        lat = params.get('lat', None)  # широта
        long = params.get('long', None)  # долгота

        if lat and long:
            pnt = Point(float(lat), float(long))
            queryset = queryset.filter(location__distance_lt=(pnt, Distance(km=10000000))).annotate(
                    distance=GeometryDistance("location", pnt)).order_by("distance")
        return queryset


class CafeDetailAPIView(LoggingMixin, generics.RetrieveAPIView):
    """ Получить полную информацию кафе по cafe_id """
    queryset = company_models.Cafe.objects.prefetch_related('week_time').select_related('company').all()
    serializer_class = mobile_serializers.CafeListSerializer
    permission_classes = (permissions.AllowAny,)
    logging_methods = ('GET',)


class UserCartAPIView(LoggingMixin, generics.RetrieveAPIView):
    """Список товаров в корзине """
    serializer_class = mobile_serializers.CartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('GET',)

    def get_object(self):
        obj, _ = order_models.Cart.objects.prefetch_related('cart_items').select_related('cafe').get_or_create(
            user=self.request.user)
        return obj


class CartItemCreateAPIView(LoggingMixin, generics.CreateAPIView):
    """
       Добавить товар в корзину
       В корзине можно хранить товары принадлежающие к одному кафе,
       Если добавить товар с другого кафе то ранние товары удаляются
    """
    serializer_class = mobile_serializers.CartItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('POST',)


class CartItemUpdateDestroyAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """
        Обновить/Удалить товар корзины
    """
    serializer_class = mobile_serializers.CartItemUpdateSerializer
    queryset = order_models.CartItem.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('PUT', 'DELETE')
    http_method_names = ('put', 'delete')


class CartEmptyAPIView(LoggingMixin, generics.GenericAPIView):
    """ Очистить корзину """
    queryset = order_models.Cart.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get',)
    logging_methods = ('GET',)

    def get_object(self):
        obj, _ = self.get_queryset().get_or_create(user=self.request.user)
        return obj

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        cart.empty_cart()
        return Response(status=status.HTTP_200_OK)


class CartAddTipAPIView(LoggingMixin, generics.GenericAPIView):
    """ Добавить tip для заказа, можно указать только одно
        значение tip или tip_percent вернет корзину пользователя
    """
    serializer_class = mobile_serializers.CartAddTipSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('POST',)
    http_method_names = ('post',)

    def get_object(self):
        user_id = self.request.user.id
        obj, _ = order_models.Cart.objects.select_related('cafe').prefetch_related(
            'cart_items').get(user_id=user_id)
        return obj

    def post(self, request, *args, **kwargs):
        try:
            cart = self.get_object()
            tip_percent = request.data.get('tip_percent', None)
            tip = request.data.get('tip', None)

            if not tip_percent and not tip:
                raise APIException('Invalid data')
            if tip_percent:
                cart.tip_percent = tip_percent
                cart.tip = round(float(cart.get_sub_total_price()) * float(tip_percent) / 100, 2)
                cart.save(update_fields=['tip', 'tip_percent'])
            elif tip and float(tip) > 0:
                cart.tip = round(float(tip), 2)
                cart.tip_percent = 0
                cart.save(update_fields=['tip', 'tip_percent'])
            serializer = mobile_serializers.CartSerializer
            return Response(serializer(cart).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FavoriteCartAPIView(LoggingMixin, generics.ListCreateAPIView):
    """ Получить список FavoriteCart """
    serializer_class = mobile_serializers.FavoriteCartSerializer
    permissions_classes = (permissions.IsAuthenticated,)
    pagination_class = MobilePagination
    logging_methods = ('GET', 'POST')

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = order_models.FavoriteCart.objects.select_related('cafe').prefetch_related(
            'favorite_cart_items').filter(user_id=user_id)
        return queryset


class FavoriteCartUpdateDestroyAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Удалить/Обновить избранные товары
    можно изменить имя и добавить адресс
    """
    queryset = order_models.FavoriteCart.objects.all()
    serializer_class = mobile_serializers.FavoriteCartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('delete', 'put')
    logging_methods = ('DELETE', 'PUT')


class FavoriteCartItemUpdateDestroyAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ Обновить/удалить Favorite cart item"""
    queryset = order_models.FavoriteCartItem.objects.all()
    serializer_class = mobile_serializers.FavoriteCartItem
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('put', 'delete')
    logging_methods = ('put', 'delete')


class FavoriteCartToCartAPIView(LoggingMixin, generics.GenericAPIView):
    """ Все товары из FavoriteCart  перенесутся в корзину """
    queryset = order_models.FavoriteCart.objects.all()
    serializer_class = mobile_serializers.CartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('GET',)
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        favorite_cart = self.get_object()
        cart = order_models.Cart.objects.get_or_create(user=request.user)
        cart.create_cart_items(favorite_cart.favorite_cart_items.all())  # Перенос товаров FavoriteCart в корзину
        cart.cafe = favorite_cart.cafe
        cart.save(update_fields=['cafe', ])
        serializer = self.get_serializer_class()
        return Response(data=serializer(cart).data, status=status.HTTP_200_OK)


class OrderToCartAPIView(LoggingMixin, generics.GenericAPIView):
    """ Все товары из Order  перенесутся в корзину """
    queryset = order_models.Order.objects.all()
    serializer_class = mobile_serializers.CartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('GET',)
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        cart = order_models.Cart.objects.get(user=request.user)
        if order.cafe and order.cafe.status == company_models.Cafe.ACTIVE:
            cart.create_cart_items(order.order_items.all())  # Перенос товаров Order в корзину
            cart.cafe = order.cafe
            cart.save(update_fields=['cafe', ])
            serializer = self.get_serializer_class()
            return Response(data=serializer(cart).data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Cafe don\'t work'}, status=status.HTTP_400_BAD_REQUEST)


class CheckOrderLimitAPIView(LoggingMixin, generics.GenericAPIView):
    """ Проверить может ли пользователь сделать заказ на время timestamp"""
    queryset = company_models.Cafe.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get',)
    logging_methods = ('GET',)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('timestamp', openapi.IN_QUERY, description="timestamp", type=openapi.TYPE_INTEGER), ])
    def get(self, request, *args, **kwargs):  # FIXME:
        cafe = self.get_object()
        if 'timestamp' not in request.query_params:  # Если не указать в параметрах timestamp
            return Response({'detail': 'add timestamp to request params'}, status=status.HTTP_400_BAD_REQUEST)

        end = datetime.datetime.fromtimestamp(int(request.query_params.get('timestamp')))
        start = end - datetime.timedelta(minutes=cafe.order_time_limit)
        now = datetime.datetime.now().date()
        orders = order_models.Order.objects.filter(created__date__gte=now)

        count = 0
        for order in orders:
            time = datetime.datetime.fromtimestamp(order.pre_order_timestamp / 1000)
            if time >= start and time <= end:
                count += 1
        if count >= cafe.order_limit:
            available = False
        else:
            available = True
        return Response({'available': available})


class UserOrderListAPIView(LoggingMixin, generics.ListAPIView):
    """Получить список всех заказов пользователя"""
    serializer_class = mobile_serializers.OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MobilePagination
    logging_methods = ('POST',)

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = order_models.Order.objects.select_related('cafe').prefetch_related(
            'order_items').filter(user_id=user_id)
        return queryset


class EmployeeGivePointToCustomerAPIView(LoggingMixin, generics.GenericAPIView):
    """ Дать point клиенту """
    queryset = user_models.User.objects.all()
    serializer_class = mobile_serializers.EmployeeGivePointSerializer
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee,)
    http_method_names = ('post',)
    logging_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                raise APIException('Invalid data')
            data = serializer.validated_data
            user = self._get_user_with_phone(data.get('phone'))
            company = mobile_logics.get_company(data.get('company'))
            self._give_point_to_user(user, company, data.get('points'))
            restapi_v2_tasks.send_notification.delay(user.id, title='test', body='test')
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _get_user_with_phone(phone: str) -> user_models.User:
        try:
            user = user_models.User.objects.get(phone=phone)
            return user
        except user_models.User.DoesNotExist:
            raise NotFound('Does not exist user')

    @staticmethod
    def _give_point_to_user(user: user_models.User,
                            company: company_models.Company, points: int):
        user_points = user.get_company_points(company)
        sum_points = points + user_points.points
        free_items_count = int(sum_points / company.exchangeable_point)
        points = sum_points - free_items_count * company.exchangeable_point
        user_points.points = points
        user_points.save(update_fields=['points', ])
        mobile_logics.save_user_free_item(user, company, free_items_count)


class EmployeeCafesListAPIView(LoggingMixin, generics.ListAPIView):
    """ Список доступных сотруднику кафе  """
    serializer_class = mobile_serializers.CafeListSerializer
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee,)
    pagination_class = MobilePagination
    logging_methods = ('GET', )

    def get_queryset(self):
        return self.request.user.employee.cafes.all()


class EmployeeUpdateOrderStatusAPIView(LoggingMixin, generics.UpdateAPIView):
    """ Изменить статус заказа """  # TODO: уведомлять пользователя при изменении статусв
    queryset = order_models.Order.objects.all()
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee,)
    serializer_class = mobile_serializers.OrderUpdateStatusSerializer
    http_method_names = ('put',)
    logging_methods = ('PUT',)


class OrderAcknowledgeAPIView(LoggingMixin, generics.GenericAPIView):
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
            mobile_logics.user_order_acknowledge(order)
        return Response(status=status.HTTP_200_OK)


class EmployeeCafeOrderDetailAPIView(LoggingMixin, generics.RetrieveAPIView):
    """ Посмотреть заказ """
    queryset = order_models.Order.objects.all()
    serializer_class = mobile_serializers.OrderForEmployeeSerializer
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee,)
    http_method_names = ('get', )
    logging_methods = ('GET', )

    def get_queryset(self):
        cafes = self.request.user.employee.cafes.all()
        if cafes.exists():
            return super().get_queryset().filter(cafe__in=cafes)
        return list()


class EmployeeCafeOrdersAPIView(LoggingMixin, generics.ListAPIView):
    """ Список заказов кафе. state: ['waiting', 'new', 'ready', 'refund', sent_out', 'delivered']  """
    queryset = order_models.Order.objects.all()
    serializer_class = mobile_serializers.OrderForEmployeeSerializer
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee,)
    pagination_class = MobilePagination
    logging_methods = ('GET',)

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


class ReadyOrderItemAPIView(LoggingMixin, generics.GenericAPIView):
    """ Готовые заказы с кухни """
    queryset = order_models.OrderItem.objects.all()
    serializer_class = mobile_serializers.ReadyOrderItemSerializer
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee, )
    http_method_names = ('post', )
    logging_methods = ('POST', )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile_logics.order_item_ready(serializer.validated_data.get('order_items'))
        return Response(status=status.HTTP_200_OK)


class CafeProductAvailableAPIView(LoggingMixin, generics.GenericAPIView):
    """ Product is_available true / false
        cafe -> int/required: id Кафе
        product -> int/required: id Продукта
        is_available -> bool/required: true - продукт есть в наличи, false - нет в наличи
    """
    queryset = product_models.Product.objects.all()
    serializer_class = mobile_serializers.CafeProductAvailableSerializer
    permission_classes = (permissions.IsAuthenticated & restapi_permissions.IsEmployee,)
    http_method_names = ('post',)
    logging_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError('Invalid data')
            cafe_id = serializer.validated_data.get('cafe')
            product_id = serializer.validated_data.get('product')
            is_available = serializer.validated_data.get('is_available')
            if is_available:
                try:
                    product_state = product_models.CafeProductState.objects.get(
                        product_id=product_id, cafe_id=cafe_id)
                    product_state.delete()
                except product_models.CafeProductState.DoesNotExist:
                    pass
            else:
                cafe = restapi_v2_logics.get_cafe(cafe_id)
                product = self.get_product(product_id)
                product_state, _ = product_models.CafeProductState.objects.get_or_create(
                    product=product, cafe=cafe)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_product(self, product_id: int) -> product_models.Product:
        try:
            product = self.get_queryset().get(pk=product_id)
            return product
        except product_models.Product.DoesNotExist:
            raise NotFound('Product does not exist')


class CafeProductsAPIView(LoggingMixin, generics.RetrieveAPIView):
    """Список всех продуктов кафе по cafe_id"""
    queryset = company_models.Cafe.objects.all()
    permission_classes = (permissions.AllowAny,)
    logging_methods = ('GET',)

    def get(self, request, *args, **kwargs):
        cafe = self.get_object()
        cache_menu_key = f'menu_{cafe.menu_id}'
        cache_menu_data = cache.get(cache_menu_key, None)
        if cache_menu_data:
            result = cache_menu_data
        else:
            not_available_product_ids = product_models.CafeProductState.objects.filter(
                cafe_id=cafe.pk).values_list('product_id', flat=True)
            context = {'request': request, 'cafe': cafe, 'not_available_product_ids': not_available_product_ids}

            categories = product_models.ProductCategory.objects.prefetch_related('children').prefetch_related(
                Prefetch('products', product_models.Product.objects.select_related('category').prefetch_related('sizes').
                         prefetch_related(Prefetch('modifiers', product_models.Modifier.objects.prefetch_related('items').all())).all())).filter(menu_id=cafe.menu_id)
            categories_header = categories.filter(parent__isnull=True)
            ready_list = list()  # Список всех товаров
            categories_header_serializer = mobile_serializers.ProductCategorySerializer(
                categories_header, context=context, many=True).data

            for category in categories_header:  # Все категории продуктов (parent == null)
                ready_list.append(self.get_category(category, context))
                if category.products.exists():
                    ready_list.append(self.get_products(category.products.all(), context))

                if category.children.exists():  # Если есть subcategory
                    for subcategory in category.children.all():
                        ready_list.append(self.get_sub_category(subcategory, context))
                        if subcategory.products.exists():
                            ready_list.append(self.get_products(subcategory.products.all(), context))

            result = {
                'version': cafe.version,
                'categories': categories_header_serializer,
                'list': ready_list
            }
            cache.set(cache_menu_key, result)
        return Response(data=result, status=status.HTTP_200_OK)

    @staticmethod
    def get_category(category: product_models.ProductCategory, context: dict) -> dict:
        return {
            'type': 0,
            'category': mobile_serializers.ProductCategorySerializer(
                category, context=context).data
        }

    @staticmethod
    def get_sub_category(subcategory: product_models.ProductCategory, context: dict) -> dict:
        return {
            'type': 1,
            'subcategory': mobile_serializers.ProductCategorySerializer(
                subcategory, context=context).data
        }

    @staticmethod
    def get_products(queryset: QuerySet, context: dict) -> dict:
        return {
            'type': 2,
            'products': mobile_serializers.ProductSerializer(
                queryset, context=context, many=True).data
        }


class CartOrderAPIView(LoggingMixin, generics.GenericAPIView):
    """
    Есть три типа оплаты: 0 = balance, 1 = online, 2 = card

    ---
    Оплата с payment_type = 0 вернет:
    {
            'payment_type': 'balance',
            'payment_status': 'paid',
            'client_secret': None,
            'cashback': cashback,
    }
    ---
    Оплата с payment_type = 1 вернет:
    {
            'payment_type': 'online',
            'payment_status': 'required_payment_method',
            'client_secret': client_secret,
            'cashback': cashback,
    }
    ---
    Оплата с payment_type = 2 вернет:
    {
            'payment_type': 'card',
            'payment_status': Тут несколько вариантов,
            'client_secret': client_secret,
            'cashback': cashback,
    }
    Если не указать или card_id = null то payment_status -> 'required_payment_method' после оплаты эта карта сохранится
    Если card_id есть то payment_status -> paid или payment_status -> required_confirm
    payment_status = required_confirm То нужно завершить платеж (карта будет спрашивать авторизацию)
    """

    serializer_class = mobile_serializers.CreateOrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('POST',)
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            cart, created = order_models.Cart.objects.get_or_create(user=user)
            serializer = self.get_serializer(data=request.data)
            if created or not cart.is_cart_valid():  # Если корзина пользователя пуста
                raise APIException('Your cart empty')
            if not serializer.is_valid(raise_exception=False):
                raise APIException('Invalid request data')
            data = serializer.validated_data
            order = mobile_logics.create_order(user, cart, data)
            card_id = data.get('card_id', None)
            if data.get('payment_type') == 0:  # Оплата с баланса
                response = self._pay_balance(user, order)
            elif data.get('payment_type') == 1:  # Оплата с карты или кошелька без сохранения карты
                response = self._pay_online(user, order)
            elif data.get('payment_type') == 2:  # Оплата сохранием карты или уже сушествуюшей карты
                response = self._pay_card(user, order, card_id)
            else:
                raise APIException('Invalid payment type')
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _pay_balance(user: user_models.User, order: order_models.Order) -> dict:
        if float(user.balance) < float(order.total_price):
            raise APIException('Не достаточно стредств для оплаты заказа')
        cashback = balance_payment_logics.pay_user_balance(  # обновит баланс и сохранит CashbackHistory
            user, order)
        mobile_logics.order_paid(order)
        mobile_logics.free_items_redeemed(order)
        mobile_logics.user_give_point(order)
        balance_payment_logics.save_order_transaction(user, order, cashback)
        return {
            'payment_type': 'balance',
            'payment_status': 'paid',
            'client_secret': None,
            'cashback': cashback,
        }

    @staticmethod
    def _pay_online(user: user_models.User, order: order_models.Order) -> dict:
        stripe.api_key = settings.STRIPE_SECRET_KEY

        customer = payment_logics.get_stripe_customer(user)

        payment_intent = stripe.PaymentIntent.create(
            amount=order.get_total_price_in_cents(),
            currency="usd",
            payment_method_types=["card"],
            customer=customer.customer_id,
            capture_method='manual',
            metadata={
                'payment_type': 'online',
                'order_id': order.id,
                'customer_id': user.id
            }
        )
        return {
            'payment_type': 'online',
            'payment_status': 'required_payment_method',
            'client_secret': payment_intent.client_secret,
            'cashback': 0,
        }

    @staticmethod
    def _pay_card(user: user_models.User, order: order_models.Order, card_id: Union[int, None]) -> dict:
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = payment_logics.get_stripe_customer(user)
            if not card_id:  # Если клиент хочет сохранить карту для следуюших оплат
                payment_intent = stripe.PaymentIntent.create(
                    amount=order.get_total_price_in_cents(),
                    currency='usd',
                    customer=customer.customer_id,
                    payment_method_types=["card"],
                    capture_method='manual',
                    setup_future_usage='off_session',
                    metadata={
                        'payment_type': 'online',
                        'order_id': order.id,
                        'customer_id': user.id
                    }
                )
                return_data = {
                    'payment_type': 'card',
                    'payment_status': 'required_payment_method',
                    'client_secret': payment_intent.client_secret,
                    'cashback': 0,
                }
            else:  # Если у клиента есть карта
                card = mobile_logics.get_user_card(card_id)
                if card.is_confirm_off_session:  # Если карту можно использовать вне сессии
                    return_data = card_logics.create_payment_intent_and_confirm_off_session(customer, card, order)
                else:  # Если катра требует дополнительных шагов авторизации
                    return_data = card_logics.create_payment_intent_and_confirm_on_session(customer, card, order)
            return return_data
        except Exception as e:
            raise APIException(str(e))









