import datetime

# LIBS
import stripe
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework_tracking.mixins import LoggingMixin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

# DJANGO
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.conf import settings
from django.utils.decorators import method_decorator
# APPS
from apps.users import logics as user_logics
from apps.users import tasks as user_tasks
from apps.users import models as user_models

from apps.payment import models as payment_models
from apps.payment.logic import charge as charge_payment_logics
from apps.payment.logic import online as online_payment_logics
from apps.payment.logic import balance as balance_payment_logics
from apps.payment.logic import logics as payment_logics

from apps.restapi import tasks as restapi_tasks
from apps.restapi.exceptions import CustomException
from apps.restapi.mobile import serializers as mobile_serializers
from apps.restapi.mobile import client_views_logic as views_logic
from apps.restapi.mobile import send_notifications
from apps.restapi import pagination

from apps.companies import models as company_models
from apps.orders import models as order_models
from apps.products import models as product_models


class RegisterLoginUserView(LoggingMixin, generics.GenericAPIView):
    """
    Регистраци и авторизация
    Если отправить только номер телефона то на номер отправляется смс код
    Если отправить смс код и номер телефона то вернет токен
    Если ключ register содержит False, надо предложить заполнить поля,
    как минимум username (API для редактирование юзера)
    """
    serializer_class = mobile_serializers.RegisterLoginUserSerializer
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
            user_logics.send_sms(user)  # TODO добавить в celery task
            return Response(data={"detail": "User created"}, status=status.HTTP_201_CREATED)
        else:
            if data.get('sms_code'):
                if int(data.get('sms_code')) == user.sms_code:
                    self.change_sms_code(user)
                    response_data = user_logics.get_tokens_for_user(user)  # вернёт dict с токенами
                    response_data['register'] = True
                    if not user.username:  # если пользователь нет минимальных данных (предложить их заполнить)
                        response_data['register'] = False
                    return Response(data=response_data, status=status.HTTP_200_OK)
                else:
                    return Response(data={"detail": "Invalid code"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_logics.send_sms(user)
                return Response(data={"detail": "SMS was sent to you"}, status=status.HTTP_200_OK)

    @staticmethod
    def change_sms_code(user: user_models.User):
        user.sms_code = 123456  # TODO: не забудь изменить его
        user.save(update_fields=['sms_code', ])


class UserRetrieveUpdateView(LoggingMixin, generics.RetrieveUpdateAPIView):
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
        obj = self.request.user
        return obj


class CafeListView(LoggingMixin, generics.ListAPIView):
    """ Список кафе
        Также можно сделать поиск по названии кафе, описании кафе и по названии компании (на всякий случай)
        Если передать в параметры местоположение вернет список кафе сортированный по дистанции от местоположения
    """
    queryset = company_models.Cafe.objects.filter(  # фильтрация статус активный, компания статус активный
        status=company_models.Cafe.ACTIVE, company__is_activate=True)
    serializer_class = mobile_serializers.CafeListSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('company__name', 'description', 'name')
    pagination_class = pagination.MyPagination
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


class UserPointsList(LoggingMixin, generics.ListAPIView):
    """User points"""
    serializer_class = mobile_serializers.PointSerializer
    queryset = user_models.Point.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.MyPagination
    logging_methods = ('GET',)

    def get_queryset(self):
        queryset = self.request.user.points.all()
        return queryset


class UserBalanceFillHistory(LoggingMixin, generics.ListAPIView):
    """ История пополнений баланса пользователя """
    queryset = user_models.BudgetFillHistory.objects.all()
    serializer_class = mobile_serializers.UserFillHistory
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.MyPagination
    logging_methods = ('GET',)

    def get_queryset(self):
        queryset = self.request.user.fill_histories.all()
        return queryset


class CafeDetailView(LoggingMixin, generics.RetrieveAPIView):
    """ Получить полную информацию кафе по cafe_id """
    queryset = company_models.Cafe.objects.all()
    serializer_class = mobile_serializers.CafeSerializer
    permission_classes = (permissions.AllowAny,)
    logging_methods = ('GET',)


class CompanyListView(LoggingMixin, generics.ListAPIView):
    """ Список компаний """
    queryset = company_models.Company.objects.all()
    serializer_class = mobile_serializers.CompanySerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = pagination.MyPagination
    logging_methods = ('GET',)


class CafeChangeFavorite(LoggingMixin, generics.GenericAPIView):
    """
        Избранные кафе пользователя добавить/удалить
        если поле is_favorite = True добавляет
        если поле is_favorite = False удаляет
    """
    queryset = company_models.Cafe.objects.all()
    serializer_class = mobile_serializers.CafeChangeFavoriteSerializer
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


class CafeProductsView(LoggingMixin, generics.RetrieveAPIView):
    """Список всех продуктов кафе по cafe_id"""
    queryset = company_models.Cafe.objects.all()
    permission_classes = (permissions.AllowAny,)
    logging_methods = ('GET',)

    def get(self, request, *args, **kwargs):
        cafe = self.get_object()
        categories = cafe.menu.categories.all().filter(available=True).order_by('position')
        categories_header = categories.filter(parent__isnull=True)
        ready_list = list()  # Список всех товаров
        for category in categories_header:  # Все категории продуктов (parent == null)

            ready_list.append({  # добавляет категорию товаров
                'type': 0,
                'category': mobile_serializers.ProductCategorySerializer(
                    category, context={'request': request}).data
            })
            if category.products.all():
                ready_list.append({  # добавляет все товары этой категории
                    'type': 2,
                    'products': mobile_serializers.ProductSerializer(
                        category.products.all(), context={'request': request}, many=True).data
                })

            if category.children.all():  # Если есть subcategory
                for subcategory in category.children.all():
                    ready_list.append({  # добавляет subcategory
                        'type': 1,
                        'subcategory': mobile_serializers.ProductCategorySerializer(
                            subcategory, context={'request': request}).data
                    })
                    if subcategory.products.all():
                        ready_list.append({  # добавляет все товары этой subcategory
                            'type': 2,
                            'products': mobile_serializers.ProductSerializer(
                                subcategory.products.all(), context={'request': request}, many=True).data
                        })
        categories_header_serializer = mobile_serializers.ProductCategorySerializer(
            categories_header, context={'request': request}, many=True)
        result = {
            'version': cafe.version,
            'categories': categories_header_serializer.data,
            'list': ready_list
        }
        return Response(data=result, status=status.HTTP_200_OK)


class CartItemCreateView(LoggingMixin, generics.CreateAPIView):
    """Добавить товар в корзину
       В корзине можно хранить товары принадлежающие к одному кафе,
       Если добавить товар с другого кафе то ранние товары удаляются
    """
    serializer_class = mobile_serializers.CartItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('POST',)


class CartItemUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """
        Обновить/Удалить товар корзины
    """
    serializer_class = mobile_serializers.CartItemSerializer
    queryset = order_models.CartItem.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('PUT', 'DELETE')
    http_method_names = ('put', 'delete')


class CartView(LoggingMixin, generics.RetrieveAPIView):
    """Список товаров в корзине """
    serializer_class = mobile_serializers.CartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('GET',)
    queryset = order_models.Cart.objects.all()

    def get_object(self):
        obj, _ = self.get_queryset().get_or_create(user=self.request.user)
        return obj


class CartAddTipView(LoggingMixin, generics.GenericAPIView):
    """ Добавить tip для заказа, можно указать только одно
        значение tip или tip_percent вернет корзину пользователя
    """
    queryset = order_models.Cart.objects.all()
    serializer_class = mobile_serializers.CartAddTipSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('POST',)
    http_method_names = ('post',)

    def get_object(self):
        obj, _ = self.get_queryset().get_or_create(user=self.request.user)
        return obj

    def post(self, request, *args, **kwargs):
        cart = self.get_object()
        tip_percent = request.data.get('tip_percent', None)
        tip = request.data.get('tip', None)

        if not tip_percent and not tip:
            return Response({'detail': 'error no tip and no tip percent'}, status=status.HTTP_400_BAD_REQUEST)
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


class CartEmptyView(LoggingMixin, generics.GenericAPIView):
    """ Удалить все товары корзины """
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


class FavoriteCartCreateView(LoggingMixin, generics.CreateAPIView):
    """
    Добавить корзину в избранные
    """
    serializer_class = mobile_serializers.CreateFavoriteCartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('GET', 'POST')


class FavoriteCartUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Удалить/Обновить избранные товары
    можно изменить имя и добавить адресс
    """
    queryset = order_models.FavoriteCart.objects.all()
    serializer_class = mobile_serializers.FavoriteCartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('delete', 'put')
    logging_methods = ('DELETE', 'PUT')


class FavoriteCartListView(LoggingMixin, generics.ListAPIView):
    """ Получить список FavoriteCart """
    serializer_class = mobile_serializers.FavoriteCartSerializer
    permissions_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.MyPagination
    logging_methods = ('GET', )

    def get_queryset(self):
        return self.request.user.favorite_carts.all()


class FavoriteCartItemUpdateDestroyView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """ Обновить/удалить Favorite cart item"""
    queryset = order_models.FavoriteCartItem.objects.all()
    serializer_class = mobile_serializers.FavoriteCartItemUpdate
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('put', 'delete')
    logging_methods = ('put', 'delete')


class FavoriteCartToCartView(LoggingMixin, generics.GenericAPIView):
    """ Все товары из FavoriteCart  перенесутся в корзину """
    queryset = order_models.FavoriteCart.objects.all()
    serializer_class = mobile_serializers.CartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('GET',)
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        favorite_cart = self.get_object()
        cart = order_models.Cart.objects.get(user=request.user)
        cart.create_cart_items(favorite_cart.favorite_cart_items.all())  # Перенос товаров FavoriteCart в корзину
        cart.cafe = favorite_cart.cafe
        cart.save(update_fields=['cafe', ])
        serializer = self.get_serializer_class()
        return Response(data=serializer(cart).data, status=status.HTTP_200_OK)


class OrderToCartView(LoggingMixin, generics.GenericAPIView):
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


class OrderListView(LoggingMixin, generics.ListAPIView):
    """Получить список всех заказов пользователя"""
    queryset = order_models.Order.objects.all()
    serializer_class = mobile_serializers.OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.MyPagination
    logging_methods = ('POST',)

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        return queryset


class CheckOrderLimitView(LoggingMixin, generics.GenericAPIView):
    """ Проверить может ли пользователь сделать заказ на время timestamp"""
    queryset = company_models.Cafe.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('timestamp', openapi.IN_QUERY, description="timestamp", type=openapi.TYPE_INTEGER),])
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


class UserFreeItemsView(LoggingMixin, generics.ListAPIView):
    """ Список всех FreeItems пользователя """
    queryset = user_models.FreeItem.objects.all()
    serializer_class = mobile_serializers.UserFreeItemsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.MyPagination
    logging_methods = ('GET',)

    def get_queryset(self):
        return self.request.user.free_items.all()


class TopUpBalanceView(LoggingMixin, generics.GenericAPIView):
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
            tariff = self.get_object()
            user = self.request.user
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid(raise_exception=False):
                raise CustomException('Invalid data')
            payment_type = serializer.validated_data.get('payment_type')
            response_data = dict()
            if payment_type == 0:  # Онлайн оплата
                response_data = balance_payment_logics.top_up_balance_online(user, tariff)
            elif payment_type == 1 and serializer.validated_data.get('card_id'):  # Оплата с карты
                card_id = serializer.validated_data.get('card_id')
                response_data = balance_payment_logics.top_up_balance_with_card(user, tariff, card_id)
            else:
                raise CustomException('Invalid payment type or invalid payment card')
            return Response(data=response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        try:
            tariff = user_models.BudgetTariff.objects.get(pk=self.request.data.get('tariff_id'))
            return tariff
        except user_models.BudgetTariff.DoesNotExist:
            raise NotFound('Tariff does not exist')


class TariffListView(LoggingMixin, generics.ListAPIView):
    """ Список тарифов для пополнения баланса (BUDGET)"""
    queryset = user_models.BudgetTariff.objects.all()
    serializer_class = mobile_serializers.TariffSerializer
    permission_classes = (permissions.AllowAny,)
    logging_methods = ('GET',)


class UserSaveCardView(LoggingMixin, generics.GenericAPIView):
    """ Сохранить карту
        вернет client_secret статус 200
        если ошибка detail': error статус 400
    """
    serializer_class = mobile_serializers.CardNameSerializer
    permission_classes = (permissions.IsAuthenticated,)
    logging_methods = ('POST',)
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            user = self.request.user
            serializer = mobile_serializers.CardNameSerializer(data=request.data)
            if not serializer.is_valid(raise_exception=False):
                raise CustomException('No cart name')
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
                usage='off_session',  # чтобы мы могли списовать деньги любое время не спрашивая у пользователя
                metadata={
                    'user_id': user.id,
                    'card_name': serializer.validated_data.get('card_name')
                }
            )
            return Response({'client_secret': setup_intent.client_secret}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserCardListView(LoggingMixin, generics.ListAPIView):
    """ Список карт пользователя """
    queryset = payment_models.CustomerCard.objects.all()
    serializer_class = mobile_serializers.UserCardSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.MyPagination
    logging_methods = ('GET',)

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        return queryset


# class PaymentOrderView(LoggingMixin, generics.GenericAPIView):
#     """ Три типа оплаты  payment_type: online = 0,  card = 1, balance = 2
#         Онлайн оплата вернёт  {'client_secret': 'xxxxxxx'}
#         Оплата с карты вернет {'detail': 'Order paid'} если удачно
#         или {'detail': 'error'}  card_id* (required)
#         Оплата с баланса вернет {'detail': 'Order paid'} если удачно
#         или {'detail': 'error'}
#     """
#     serializer_class = mobile_serializers.CreateOrderSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#     logging_methods = ('POST',)
#     http_method_names = ('post',)
#
#     def post(self, request, *args, **kwargs):  # FIXME
#
#         try:
#             user = self.request.user
#             cart = user.cart
#             serializer = mobile_serializers.CreateOrderSerializer(data=request.data)
#             if not serializer.is_valid(raise_exception=False):
#                 return Response({'detail': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)
#             # serializer.is_valid(raise_exception=True)
#             data = serializer.validated_data
#             if self.is_cart_empty(cart):  # Проверка корзины (не пустая ли корзина)
#                 return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
#             order = views_logic.create_order(user, cart, data)
#             payment_type = data.get('payment_type')
#             # cart.empty_cart()
#             if payment_type == 0:  # Оплата заказа онлайн
#                 return self.payment_online(order)
#
#             elif payment_type == 1:  # Оплата с карты пользователя
#                 return self.payment_card(order, data, user)
#
#             elif payment_type == 2:  # Оплата с баланса пользователя
#                 return self.payment_balance(order, user)
#             else:
#                 return Response({'detail': 'Error'}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#     @staticmethod
#     def payment_online(order):
#         try:
#             stripe.api_key = settings.STRIPE_SECRET_KEY
#             payment_intent = stripe.PaymentIntent.create(
#                 payment_method_types=['card'],
#                 amount=order.get_total_price_in_cents(),   # сумма заказа в центах 22 22
#                 currency='usd',  # Курс в долларах
#                 capture_method='manual',
#                 metadata={
#                     'type': 'online',
#                     'order_id': order.id,
#                     'user_id': order.user.id
#                 }
#             )
#             data = {
#                 'client_secret': payment_intent.client_secret,  # для завершения оплаты на моб. устройстве
#             }
#
#             return Response(data, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#     @staticmethod
#     def payment_card(order, data, user):
#         try:
#             stripe.api_key = settings.STRIPE_SECRET_KEY
#             payment_type = payment_models.OrderPaymentTransaction.CARD
#             card = payment_logics.get_card(data.get('card_id'))
#             transactions = payment_models.OrderPaymentTransaction.objects.filter(
#                 user=user, payment_type=payment_type, card=card, is_capture=False)
#             if charge_payment_logics.check_charges_limit(order, transactions):
#                 try:
#
#                     charges_amount, _metadata = charge_payment_logics.charge_canceled_and_get_amount(transactions)
#                     total_amount = order.get_total_price_in_cents() + charges_amount
#                     _metadata['user_id'] = user.id
#                     _metadata['type'] = 'card'
#                     _metadata['order_id'] = order.id
#
#                     payment_intent = stripe.PaymentIntent.create(
#                         amount=total_amount,
#                         currency='usd',
#                         customer=user.stripe_customer.customer_id,
#                         payment_method=card.card_id,
#                         confirm=True,
#                         off_session=True,
#                         metadata=_metadata
#                     )
#                     if payment_intent.status == 'succeeded':
#                         transaction = charge_payment_logics.create_order_transaction_card(order, card, payment_intent)
#                         views_logic.order_paid(order)
#                         views_logic.user_give_point(order)
#                         if transactions:
#                             for _transaction in transactions:
#                                 _transaction.final_transaction = transaction
#                                 _transaction.save(update_fields=['final_transaction', ])
#                         views_logic.free_items_redeemed(order)
#                         user.cart.empty_cart()
#                         return Response({'detail': 'Paid'}, status=status.HTTP_200_OK)
#
#                 except Exception as e:
#                     return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 try:
#                     payment_intent = stripe.PaymentIntent.create(
#                         amount=order.get_total_price_in_cents(),
#                         currency='usd',
#                         customer=user.stripe_customer.customer_id,
#                         payment_method=card.card_id,
#                         capture_method='manual',
#                         confirm=True,
#                         off_session=True,
#                         metadata={
#                             'type': 'card',
#                             'order_id': order.id,
#                             'user_id': user.id,
#                             'card_id': card.id
#                         })
#                 except Exception as e:
#                     return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#                 if payment_intent.status == 'requires_capture':
#                     _ = charge_payment_logics.create_order_transaction_card(order, card, payment_intent)
#                     views_logic.order_paid(order)
#                     views_logic.user_give_point(order)
#                     views_logic.free_items_redeemed(order)
#                     user.cart.empty_cart()
#                     return Response({'detail': 'Paid'}, status=status.HTTP_200_OK)
#
#                 else:
#                     return Response({'detail': str(payment_intent.status)}, status=status.HTTP_400_BAD_REQUEST)
#
#         except Exception as e:
#             return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#     @staticmethod
#     def payment_balance(order, user):  # оплата с баланса
#         try:
#             if user.get_balance_in_cents() >= order.get_total_price_in_cents():  # если хватает средств для оплаты
#                 cashback = balance_payment_logics.get_cashback(order)  # только для типа оплаты balance
#                 balance_payment_logics.create_order_transaction_balance(  # Сохраняет транзакцию
#                    order=order, cashback=cashback)
#                 balance_payment_logics.user_update_balance(  # обноаляет баланс клиента
#                     user, order, cashback)
#                 balance_payment_logics.save_cashback_history(  # сохраняет кешбэк
#                     user, order, cashback)
#                 views_logic.order_paid(order)  # изменяет статус заказа на PAID
#                 views_logic.user_give_point(order)  # сохранят баллы клиета
#                 views_logic.free_items_redeemed(order)
#                 response = {
#                     'detail': 'order paid',
#                     'cashback': cashback,
#                 }
#                 user.cart.empty_cart()
#                 return Response(response, status=status.HTTP_201_CREATED)
#
#             else:
#                 return Response({'detail': 'you do not have enough funds on your balance'})
#
#         except Exception as e:
#             return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#     @staticmethod
#     def is_cart_empty(cart):
#         if not cart.cafe or not cart.cart_items.all():
#             return True
#         return False


# class PaymentOrderView(LoggingMixin, generics.GenericAPIView):
#     """ Три типа оплаты  payment_type: online = 0,  card = 1, balance = 2
#      Онлайн оплата вернёт  {'client_secret': 'xxxxxxx'}
#      Оплата с карты вернет {'detail': 'Order paid'} если удачно
#      или {'detail': 'error'}  card_id* (required)
#      Оплата с баланса вернет {'detail': 'Order paid'} если удачно
#      или {'detail': 'error'}
#     """
#     serializer_class = mobile_serializers.CreateOrderSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     logging_methods = ('POST', )
#     http_method_names = ('post', )
#
#     def post(self, request, *args, **kwargs):
#         try:
#             user = request.user
#             cart = user.cart
#             serializer = self.get_serializer(data=request.data)
#             if not serializer.is_valid(raise_exception=False):
#                 raise CustomException('Invalid data')
#             if not self._cart_is_valid(cart):  # Проверка не пуста ли корзина
#                 raise CustomException('Your cart empty')
#             data = serializer.validated_data
#             order = views_logic.create_order(user, cart, data)
#             if data.get('payment_type') == 0:  # Онлайн оплата
#                 response_data = self._payment_online(user, order)
#             elif data.get('payment_type') == 1:  # Оплата с сохраненной карты
#                 response_data = self._payment_with_save_card(user, order, data.get('card_id'))
#             elif data.get('payment_type') == 2:  # Оплата с баланса пользователя
#                 response_data = self._payment_with_balance(user, order)
#             else:
#                 raise CustomException('invalid payment type')
#
#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#     @staticmethod
#     def _cart_is_valid(cart: order_models.Cart) -> bool:
#         if cart.cafe and cart.cart_items.all():
#             return True
#         return False
#
#     @staticmethod
#     def _payment_online(user: user_models.User, order: order_models.Order) -> dict:
#         try:
#             stripe.api_key = settings.STRIPE_SECRET_KEY
#             payment_intent = stripe.PaymentIntent.create(
#                 payment_method_types=['card'],
#                 amount=order.get_total_price_in_cents(),  # сумма заказа в центах
#                 currency='usd',  # Курс в долларах
#                 capture_method='manual',  # замараживает деньги (нужно захватить средства в течени 7 дней)
#                 metadata={
#                     'type': 'online',
#                     'order_id': order.id,
#                     'user_id': user.id
#                 }
#             )
#             response_data = {
#                 'client_secret': payment_intent.client_secret,  # для завершения оплаты на моб. устройстве
#             }
#             return response_data
#         except Exception as e:
#             raise CustomException(str(e))
#
#     @staticmethod
#     def _payment_with_save_card(user: user_models.User, order: order_models.Order, card_id: int) -> dict:
#         try:
#             stripe.api_key = settings.STRIPE_SECRET_KEY
#             card = payment_logics.get_card(card_id)
#             capture_method, is_capture = charge_payment_logics.get_capture_method(user)
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=order.get_total_price_in_cents(),
#                 currency='usd',
#                 customer=user.stripe_customer.customer_id,
#                 payment_method=card.card_id,
#                 capture_method=capture_method,
#                 confirm=True,
#                 off_session=True,
#                 metadata={
#                     'type': 'card',
#                     'order_id': order.id,
#                     'user_id': user.id,
#                     'card_id': card.id
#                 })
#             if payment_intent.status == 'requires_capture' or payment_intent.status == 'succeeded':
#                 charge_payment_logics.create_order_transaction_card(order, card, payment_intent.id, is_capture)
#                 views_logic.order_paid(order)
#                 views_logic.user_give_point(order)
#                 views_logic.free_items_redeemed(order)
#                 user.cart.empty_cart()
#
#                 return {'detail': 'Paid'}
#             else:
#                 raise CustomException('error client_views 901')
#
#         except Exception as e:
#             raise CustomException(str(e))
#
#     @staticmethod
#     def _payment_with_balance(user: user_models.User, order: order_models.Order) -> dict:
#         try:
#             if order.get_total_price_in_cents() > user.get_balance_in_cents():
#                 raise CustomException('not enough funds to pay')
#             cashback = balance_payment_logics.get_cashback(order)
#             balance_payment_logics.create_order_transaction_balance(  # Сохраняет транзакцию
#                order=order, cashback=cashback)
#             balance_payment_logics.user_update_balance(  # обноаляет баланс клиента
#                 user, order, cashback)
#             views_logic.order_paid(order)  # изменяет статус заказа на PAID
#             views_logic.user_give_point(order)  # сохранят баллы клиета
#             views_logic.free_items_redeemed(order)  # сохраняет использованные free item
#             user.cart.empty_cart()
#             return {'detail': 'Paid'}
#         except Exception as e:
#             raise CustomException(str(e))


class UserCardUpdateDeleteView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """Удалить/изменить карту пользователя"""
    queryset = payment_models.CustomerCard.objects.all()
    serializer_class = mobile_serializers.UpdateUserCardSerializer
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
    def _get_charges_card(card: payment_models.CustomerCard) -> list:  # замароженные транзакции
        charges = payment_models.OrderPaymentTransaction.objects.filter(
            card=card, is_capture=False)
        return charges

    @staticmethod
    def _capture_charge(transaction: payment_models.OrderPaymentTransaction):  # захват средств
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            payment_intent = stripe.PaymentIntent.capture(
                transaction.payment_id)
            if payment_intent.status == 'succeeded':
                transaction.is_capture = True
                transaction.save(update_fields=['is_capture', ])
            else:
                raise CustomException('error  client_views 891')
        except Exception as e:
            raise CustomException(str(e))

    @staticmethod
    def _delete_card_in_stripe(card_id: str):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            pm = stripe.PaymentMethod.detach(
                card_id,
            )
            print(pm)
        except Exception as e:
            raise CustomException(str(e))


class CompanyRetrieveView(LoggingMixin, generics.RetrieveAPIView):
    """ Компания """
    queryset = company_models.Company.objects.all()
    serializer_class = mobile_serializers.CompanySerializer
    permission_classes = (permissions.AllowAny,)
    logging_methods = ('GET', )


class CompanyCafesView(LoggingMixin, generics.ListAPIView):
    """ Другие кафе компании """
    queryset = company_models.Cafe.objects.all()
    serializer_class = mobile_serializers.CafeListSerializer
    permission_classes = (permissions.AllowAny,)
    logging_methods = ('GET',)

    def get_queryset(self):
        try:
            cafe = super().get_queryset().get(pk=self.kwargs.get(self.lookup_field))
            queryset = super().get_queryset().filter(company=cafe.company).exclude(pk=cafe.id)
        except company_models.Cafe.DoesNotExist:
            queryset = list()
        return queryset


class UserNotificationView(LoggingMixin, generics.ListAPIView):
    """ Уведомления пользователя """
    queryset = user_models.UserNotification.objects.all()
    serializer_class = mobile_serializers.UserNotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.MyPagination
    logging_methods = ('GET',)

    def get_queryset(self):
        queryset = self.request.user.notifications.all()
        return queryset


