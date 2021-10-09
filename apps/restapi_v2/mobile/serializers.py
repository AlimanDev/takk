from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField
from rest_framework.exceptions import ValidationError
from apps.companies import models as company_models
from apps.products import models as product_models
from apps.users import models as user_models
from apps.orders import models as order_models
from apps.restapi.mobile import serializer_logics
from apps.payment import models as payment_models
from apps.restapi_v2 import serializers as restapi_v2_serializer


class UserAuthSerializer(serializers.Serializer):
    phone = serializers.CharField()
    sms_code = serializers.CharField(required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields = (
            'id', 'username', 'phone',
            'user_type', 'date_of_birthday',
            'avatar', 'referral_code', 'balance')
        extra_kwargs = {
            'balance': {'read_only': True},
            'phone': {'read_only': True},
            'user_type': {'read_only': True},
            'referral_code': {'read_only': True},
        }


class UserPointSerializer(serializers.ModelSerializer):
    company = restapi_v2_serializer.CompanyMinDataSerializer(read_only=True)

    class Meta:
        model = user_models.Point
        fields = ('id', 'company', 'points')


class UserNotificationSerializer(serializers.ModelSerializer):
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)

    class Meta:
        model = user_models.UserNotification
        fields = ('id', 'title', 'body', 'created_dt')


class UserFillHistorySerializer(serializers.ModelSerializer):
    created_dt = serializers.IntegerField(read_only=True, source='get_created_dt_timestamp')

    class Meta:
        model = user_models.BudgetFillHistory
        fields = ('id', 'amount_payout', 'amount_receipt', 'created_dt')


class UserFreeItemsSerializer(serializers.ModelSerializer):
    company = restapi_v2_serializer.CompanyMinDataSerializer(read_only=True)
    product = serializers.SerializerMethodField()
    expiration_dt = serializers.IntegerField(read_only=True, source='get_expiration_dt_timestamp')
    created_dt = serializers.IntegerField(read_only=True, source='get_created_dt_timestamp')

    class Meta:
        model = user_models.FreeItem
        fields = ('id', 'company', 'product', 'created_dt', 'expiration_dt', 'status')

    def get_product(self, obj):
        if obj.product:
            info = {
                'id': obj.product_id,
                'name': obj.product.name,
            }
            return info
        return None


class UserCardSerializer(serializers.ModelSerializer):
    created_dt = serializers.IntegerField(read_only=True, source='get_created_dt_timestamp')

    class Meta:
        model = payment_models.CustomerCard
        fields = ('id', 'brand', 'last4', 'name', 'created_dt')


class UserCardCreateSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=4, max_length=50, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.save(update_fields=['name', ])
        return instance


class TopUpBalanceSerializer(serializers.Serializer):
    tariff_id = serializers.IntegerField(required=True)
    payment_type = serializers.IntegerField(required=True)
    card_id = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CafeWeekTimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = company_models.CafeWeekTime
        fields = ('id', 'day', 'is_open', 'opening_time', 'closing_time')


class CafePhotoSerializer(serializers.ModelSerializer):
    image_small = serializers.ImageField()

    class Meta:
        model = company_models.CafePhoto
        fields = ('image', 'image_small')


class CafeListSerializer(serializers.ModelSerializer):
    logo_medium = serializers.ImageField()
    logo_small = serializers.ImageField()
    logo_large = serializers.ImageField()
    is_open_now = serializers.BooleanField(source='get_is_open_now')
    opening_time = serializers.TimeField(source='get_opening_time')
    closing_time = serializers.TimeField(source='get_closing_time')
    is_favorite = serializers.SerializerMethodField()
    photos = CafePhotoSerializer(many=True)
    working_days = CafeWeekTimeSerializer(many=True, source='week_time')
    cafe_timezone = TimeZoneSerializerField()

    class Meta:
        model = company_models.Cafe
        fields = '__all__'

    def get_is_favorite(self, obj):  # Избранные кафе пользователя
        is_favorite = False
        if self.context['request'].user.is_authenticated:
            favorite_cafes = self.context['request'].user.favorite_cafes.all().values_list('id', flat=True)
            if obj.pk in favorite_cafes:
                is_favorite = True
        return is_favorite


class UserCafeFavoriteSerializer(serializers.Serializer):
    is_favorite = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CafeMinDataSerializer(serializers.ModelSerializer):
    logo_small = serializers.ImageField()

    class Meta:
        model = company_models.Cafe
        fields = ('id', 'name', 'logo_small', 'location', 'address', 'second_address')
        read_only_fields = ('id', 'name', 'logo_small', 'location', 'address', 'second_address')


class CartItemSerializer(serializers.ModelSerializer):
    cafe = serializers.IntegerField(write_only=True, required=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_price')
    modifiers_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_modifiers_price')
    sub_total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_total_price')
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_price')
    total_tax = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_total_tax_price')

    class Meta:
        model = order_models.CartItem
        fields = (
            'id', 'cafe', 'product', 'product_size', 'product_modifiers',
            'product_name', 'product_price', 'modifiers_price', 'sub_total_price',
            'total_price', 'instruction', 'quantity', 'total_tax'
        )

    def create(self, validated_data):
        user = self.context.get('request').user
        cafe = company_models.Cafe.objects.get(pk=validated_data['cafe'])  # FIXME: тут нужно добавить обработку ошибки
        cart, created = order_models.Cart.objects.get_or_create(user=user)
        if not created:
            if not cart.cafe_id == cafe.pk:  # Проверка кафе товара
                cart.empty_cart()
        cart.cafe = cafe
        cart.save()
        validated_data.pop('cafe')
        validated_data['cart'] = cart
        instance = super().create(validated_data)
        return instance


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, source='cart_items')
    sub_total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_sub_total_price')
    tax_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_tax_total')
    free_items = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_free_items_price')
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_price')
    total_price_with_free_items = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_price_with_free_items')
    cafe = CafeMinDataSerializer(read_only=True)
    tax = serializers.DecimalField(
        max_digits=10, decimal_places=3, read_only=True, source='get_cafe_products_tax')

    class Meta:
        model = order_models.Cart
        fields = (
            'id', 'cafe', 'tip', 'tip_percent',
            'items', 'sub_total_price', 'tax_total', 'free_items',
            'total_price', 'total_price_with_free_items', 'tax'
        )


class CartItemUpdateSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_price')
    modifiers_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_modifiers_price')
    sub_total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_total_price')
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_price')
    total_tax = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_total_tax_price')

    class Meta:
        model = order_models.CartItem
        fields = (
            'id', 'product', 'product_size', 'product_modifiers',
            'product_name', 'product_price', 'modifiers_price', 'sub_total_price',
            'total_price', 'instruction', 'quantity', 'total_tax'
        )
        read_only_fields = ('product',)


class CartAddTipSerializer(serializers.Serializer):
    tip = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    tip_percent = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class DeliverySerializer(serializers.ModelSerializer):

    class Meta:
        model = order_models.Delivery
        fields = (
            'id', 'address', 'latitude',
            'longitude', 'instruction', 'price',
                  )
        extra_kwargs = {
            'price': {'read_only': True},
        }


class FavoriteCartItem(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_price')
    modifiers_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_modifiers_price')
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_total_price')

    class Meta:
        model = order_models.FavoriteCartItem
        fields = (
            'id', 'product', 'product_size',
            'product_modifiers', 'instruction', 'quantity',
            'product_name', 'product_price', 'modifiers_price',
            'total_price'
        )
        read_only_fields = ('product',)


class FavoriteCartSerializer(serializers.ModelSerializer):
    cafe = CafeMinDataSerializer(read_only=True)
    items = FavoriteCartItem(many=True, read_only=True, source='favorite_cart_items')
    delivery = DeliverySerializer(required=False, allow_null=True)
    sub_total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_sub_total_price')

    class Meta:
        model = order_models.FavoriteCart
        fields = (
            'id', 'cafe', 'delivery',
            'sub_total_price', 'items', 'name'
        )
        read_only_fields = ('cafe',)

    def create(self, validated_data):
        user = self.context['request'].user
        cart = user.cart
        instance = order_models.FavoriteCart()
        instance.name = validated_data['name']
        instance.cafe = cart.cafe
        instance.user = user
        delivery = serializer_logics.delivery_saver(
            validated_data.get('delivery', False), user, cart.cafe)
        if delivery:  # если есть адресс доставки то сохраняет его
            instance.delivery = delivery
        instance.save()
        serializer_logics.cart_items_saver(cart.cart_items.all(), instance)
        return instance

    def update(self, instance, validated_data):
        if validated_data.get('name'):
            instance.name = validated_data.get('name')
        delivery = serializer_logics.delivery_saver(validated_data.get('delivery', False), instance.user,
                                                    instance.cafe)
        if delivery:
            if instance.delivery:
                old_delivery = instance.delivery
                old_delivery.delete()
            instance.delivery = delivery
        instance.save()
        return instance


class ModifiersItemMinData(serializers.ModelSerializer):
    class Meta:
        model = product_models.ModifierItem
        fields = ('id', 'name', 'price')


class OrderItemSerializer(serializers.ModelSerializer):
    product_modifiers = ModifiersItemMinData(many=True, read_only=True)

    class Meta:
        model = order_models.OrderItem
        fields = (
            'id', 'product', 'product_size',
            'product_modifiers', 'quantity', 'product_name',
            'product_price', 'modifiers_price', 'sub_total_price',
            'total_price', 'instruction', 'is_free',
            'free_count', 'free_price', 'tax_percent',
            'tax_rate'
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='order_items')
    delivery = DeliverySerializer(required=False, allow_null=True)
    cafe = CafeMinDataSerializer(read_only=True)
    updated = serializers.IntegerField(source='get_updated_timestamp')
    created = serializers.IntegerField(source='get_created_timestamp')

    class Meta:
        model = order_models.Order
        fields = (
            'id', 'cafe', 'delivery',
            'sub_total_price', 'tax_total', 'total_price',
            'free_items', 'status', 'pre_order_timestamp',
            'tip', 'tip_percent', 'updated', 'created', 'items'
        )
        extra_kwargs = {
            'sub_total_price': {'read_only': True},
            'tax_total': {'read_only': True},
            'total_price': {'read_only': True},
            'status': {'read_only': True}
        }


class EmployeeGivePointSerializer(serializers.Serializer):
    points = serializers.IntegerField(required=True)
    phone = serializers.CharField(required=True)
    company = serializers.IntegerField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class OrderUpdateStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = order_models.Order
        fields = ('status', )

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status')
        instance.save(update_fields=['status', ])
        return instance


class UserMinInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields = ('id', 'phone', 'username', 'avatar')


class OrderItemForEmployeeSerializer(serializers.ModelSerializer):
    product_modifiers = ModifiersItemMinData(many=True, read_only=True)

    class Meta:
        model = order_models.OrderItem
        fields = '__all__'  # TODO: написать все ключи


class OrderForEmployeeSerializer(serializers.ModelSerializer):

    delivery = DeliverySerializer(required=False, allow_null=True)
    cafe = CafeMinDataSerializer(read_only=True)
    user = UserMinInfoSerializer(read_only=True)
    is_kitchen = serializers.SerializerMethodField(read_only=True)
    main = serializers.SerializerMethodField(read_only=True)
    kitchen = serializers.SerializerMethodField(read_only=True)
    created = serializers.IntegerField(read_only=True, source='get_created_timestamp')
    updated = serializers.IntegerField(read_only=True, source='get_updated_timestamp')

    class Meta:
        model = order_models.Order
        fields = '__all__'  # TODO: написать все ключи
        extra_kwargs = {
            'sub_total_price': {'read_only': True},
            'tax_total': {'read_only': True},
            'total_price': {'read_only': True},
            'status': {'read_only': True}
        }

    @staticmethod
    def get_is_kitchen(obj):
        items = obj.order_items.all().filter(product__category__is_kitchen=True)
        if items:
            return True
        return False

    @staticmethod
    def get_main(obj):
        queryset = obj.order_items.all().filter(product__category__is_kitchen=False)
        return OrderItemForEmployeeSerializer(queryset, many=True).data

    @staticmethod
    def get_kitchen(obj):
        queryset = obj.order_items.all().filter(product__category__is_kitchen=True)
        return OrderItemForEmployeeSerializer(queryset, many=True).data


class ReadyOrderItemSerializer(serializers.Serializer):

    order_items = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CafeProductAvailableSerializer(serializers.Serializer):
    product = serializers.IntegerField(required=True)
    cafe = serializers.IntegerField(required=True)
    is_available = serializers.BooleanField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductSize(serializers.ModelSerializer):

    class Meta:
        model = product_models.ProductSize
        fields = ('id', 'name', 'price', 'default', 'available')


class ModifierItem(serializers.ModelSerializer):

    class Meta:
        model = product_models.ModifierItem
        fields = ('id', 'name', 'price', 'default', 'available')


class Modifier(serializers.ModelSerializer):
    items = ModifierItem(many=True)

    class Meta:
        model = product_models.Modifier
        fields = ('id', 'name', 'is_single', 'required', 'available', 'items')


class ProductCategorySerializer(serializers.ModelSerializer):
    image_medium = serializers.ImageField()
    start = serializers.TimeField(source='get_start_time')
    end = serializers.TimeField(source='get_end_time')

    class Meta:
        model = product_models.ProductCategory
        fields = ('id', 'name', 'image_medium', 'start', 'end')


class ProductSerializer(serializers.ModelSerializer):
    image_small = serializers.ImageField()
    image_medium = serializers.ImageField()
    image_large = serializers.ImageField()
    modifiers = Modifier(many=True)
    sizes = ProductSize(many=True)
    category = ProductCategorySerializer()
    start = serializers.TimeField(source='get_start_time')
    end = serializers.TimeField(source='get_end_time')

    class Meta:
        model = product_models.Product
        fields = (
            'id', 'category', 'modifiers', 'image',
            'image_small', 'image_medium', 'image_large', 'name',
            'description', 'position', 'start', 'end',
            'quickest_time', 'tax_percent', 'sizes', 'modifiers'
        )

    def get_available(self, obj) -> bool:
        not_available_product_ids = self.context.get('not_available_product_ids')
        if obj.id in not_available_product_ids:
            return False
        return True


class CreateOrderSerializer(serializers.Serializer):
    # delivery = DeliverySerializer(required=False, allow_null=True)
    pre_order_timestamp = serializers.IntegerField(required=True)
    payment_type = serializers.IntegerField(required=True)
    card_id = serializers.IntegerField(required=False, allow_null=True)
    use_free_items = serializers.BooleanField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RefundPaymentOrderSerializer(serializers.Serializer):
    order_refund = serializers.BooleanField(required=False, allow_null=True)
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True, required=False)
    items = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, required=False)
    description = serializers.CharField(
        max_length=1000, required=True)


    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
