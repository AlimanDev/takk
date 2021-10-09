from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField
from rest_framework.exceptions import ValidationError
from apps.companies import models as company_models
from apps.products import models as product_models
from apps.users import models as user_models
from apps.orders import models as order_models
from apps.restapi.mobile import serializer_logics
from apps.payment import models as payment_models


class RegisterLoginUserSerializer(serializers.Serializer):
    phone = serializers.CharField()
    sms_code = serializers.CharField(required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields = [
            'id', 'username', 'date_of_birthday', 'phone',
            'avatar', 'referral_code', 'balance',
            'user_type'
        ]
        read_only_fields = ('phone', 'referral_code', 'balance', 'id', 'user_type')


class CafeMinDataSerializer(serializers.ModelSerializer):
    logo_small = serializers.ImageField()

    class Meta:
        model = company_models.Cafe
        fields = ('id', 'name', 'logo_small', 'location', 'address', 'second_address')


class CafeWeekTimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = company_models.CafeWeekTime
        exclude = ('id', 'cafe')


class CafePhotoSerializer(serializers.ModelSerializer):
    image_small = serializers.ImageField()

    class Meta:
        model = company_models.CafePhoto
        fields = ('image', 'image_small')


class CafeSerializer(serializers.ModelSerializer):
    is_open_now = serializers.BooleanField(source='get_is_open_now')
    photos = CafePhotoSerializer(many=True)
    working_days = CafeWeekTimeSerializer(many=True, source='week_time')
    cafe_timezone = TimeZoneSerializerField()
    logo_medium = serializers.ImageField()
    logo_small = serializers.ImageField()
    logo_large = serializers.ImageField()

    class Meta:
        model = company_models.Cafe
        fields = '__all__'


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


class CafeChangeFavoriteSerializer(serializers.Serializer):
    is_favorite = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CompanySerializer(serializers.ModelSerializer):
    cafes = CafeMinDataSerializer(many=True)
    logo_resized = serializers.ImageField()

    class Meta:
        model = company_models.Company
        fields = (
            'id', 'name', 'logo', 'logo_resized', 'loading_app_image', 'app_image_morning',
            'app_image_day', 'app_image_evening', 'about', 'cafes')


class ProductSize(serializers.ModelSerializer):

    class Meta:
        model = product_models.ProductSize
        fields = '__all__'


class ModifierItem(serializers.ModelSerializer):

    class Meta:
        model = product_models.ModifierItem
        exclude = ('modifier',)


class Modifier(serializers.ModelSerializer):
    items = ModifierItem(many=True)

    class Meta:
        model = product_models.Modifier
        exclude = ('menu', )


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
        exclude = ('cart',)

    def create(self, validated_data):
        user = self.context.get('request').user
        cafe = company_models.Cafe.objects.get(pk=validated_data['cafe'])
        cart, created = order_models.Cart.objects.get_or_create(user=user)
        if not created:
            if not cart.cafe == cafe:  # Проверка кафе товара
                for item in cart.cart_items.all():  # если добавляемый товар относится к другому кафе то
                    item.delete()                   # ранние товары удаляются с корзины
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
        exclude = ('user',)


class UserFavoriteCafeSerializer(serializers.Serializer):
    cafe = serializers.IntegerField(required=True)
    is_add = serializers.BooleanField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class DeliverySerializer(serializers.ModelSerializer):

    class Meta:
        model = order_models.Delivery
        exclude = ('user', )
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
        fields = '__all__'


class FavoriteCartItemUpdate(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_price')
    modifiers_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_modifiers_price')
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_product_total_price')

    class Meta:
        model = order_models.FavoriteCartItem
        fields = '__all__'
        read_only_fields = (
            'id', 'favorite_cart', )

    # def update(self, instance, validated_data):
    #
    #     if validated_data.get('quantity'):
    #         instance.quantity = validated_data.get('quantity')
    #         instance.save(update_fields=['quantity', ])
    #     return instance


class FavoriteCartSerializer(serializers.ModelSerializer):
    items = FavoriteCartItem(many=True, read_only=True, source='favorite_cart_items')
    delivery = DeliverySerializer(required=False, allow_null=True)
    sub_total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_sub_total_price')
    cafe = CafeMinDataSerializer(read_only=True)

    class Meta:
        model = order_models.FavoriteCart
        exclude = ('user',)
        extra_kwargs = {
            'id': {'read_only': True},
        }


class CreateFavoriteCartSerializer(serializers.ModelSerializer):
    items = FavoriteCartItem(many=True, read_only=True, source='favorite_cart_items')
    delivery = DeliverySerializer(required=False, allow_null=True)
    sub_total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_sub_total_price')

    class Meta:
        model = order_models.FavoriteCart
        exclude = ('user', )
        extra_kwargs = {
            'id': {'read_only': True},
            'cafe': {'read_only': True},
        }

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
    available = serializers.SerializerMethodField()

    class Meta:
        model = product_models.Product
        fields = '__all__'

    def get_available(self, obj):
        return True

class ModifiersItemMinData(serializers.ModelSerializer):
    class Meta:
        model = product_models.ModifierItem
        fields = ('id', 'name', 'price')


class OrderItemSerializer(serializers.ModelSerializer):
    product_modifiers = ModifiersItemMinData(many=True, read_only=True)

    class Meta:
        model = order_models.OrderItem
        exclude = ('is_ready', )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='order_items')
    delivery = DeliverySerializer(required=False, allow_null=True)
    cafe = CafeMinDataSerializer(read_only=True)

    class Meta:
        model = order_models.Order
        exclude = ('user',)
        extra_kwargs = {
            'sub_total_price': {'read_only': True},
            'tax_total': {'read_only': True},
            'total_price': {'read_only': True},
            'status': {'read_only': True}
        }


class UserMinInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields = ('id', 'phone', 'username', 'avatar')


class OrderItemForEmployeeSerializer(serializers.ModelSerializer):
    product_modifiers = ModifiersItemMinData(many=True, read_only=True)

    class Meta:
        model = order_models.OrderItem
        fields = '__all__'


class OrderForEmployeeSerializer(serializers.ModelSerializer):
    # items = OrderItemSerializer(many=True, read_only=True, source='order_items')
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
        fields = '__all__'
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


class CreateOrderSerializer(serializers.Serializer):
    delivery = DeliverySerializer(required=False, allow_null=True)
    pre_order_timestamp = serializers.IntegerField(required=True)
    payment_type = serializers.IntegerField(required=True)
    card_id = serializers.IntegerField(required=False, allow_null=True)
    use_free_items = serializers.BooleanField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserFreeItemsSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = user_models.FreeItem
        exclude = ('user', )


class StripeCustomerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = payment_models.StripeCustomer
        exclude = ('customer_id',)


class TariffSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.BudgetTariff
        fields = '__all__'


class CompanyForPointSerializer(serializers.ModelSerializer):
    logo_resized = serializers.ImageField()

    class Meta:
        model = company_models.Company
        fields = ('id', 'name', 'logo', 'logo_resized')


class PointSerializer(serializers.ModelSerializer):
    company = CompanyForPointSerializer()

    class Meta:
        model = user_models.Point
        exclude = ('user', 'created_at')


class UserFillHistory(serializers.ModelSerializer):

    class Meta:
        model = user_models.BudgetFillHistory
        exclude = ('user', 'transaction', 'tariff')


class OrderUpdateStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = order_models.Order
        fields = ('status', )

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status')
        instance.save(update_fields=['status', ])
        return instance


class UserCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = payment_models.CustomerCard
        fields = ('id', 'brand', 'last4', 'name')
        read_only_fields = ('id', 'brand', 'last4')

    def update(self, instance, validated_data):
        if validated_data.get('name', False):
            instance.name = validated_data['name']
            instance.save(update_fields=['name', ])
        return instance


class CardNameSerializer(serializers.Serializer):
    card_name = serializers.CharField(max_length=50, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PaymentCardSerializer(serializers.Serializer):
    card_id = serializers.IntegerField(required=True)
    order_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CartAddTipSerializer(serializers.Serializer):
    tip = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    tip_percent = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class TopUpBalanceSerializer(serializers.Serializer):
    tariff_id = serializers.IntegerField(required=True)
    payment_type = serializers.IntegerField(required=True)
    card_id = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class EmployeeProductStatusUpdateSerializer(serializers.Serializer):
    available = serializers.BooleanField(required=True)

    def update(self, instance, validated_data):
        instance.available = validated_data.get('available')
        instance.save(update_fields=['available', ])
        return instance

    def create(self, validated_data):
        pass


class RefundPaymentOrderSerializer(serializers.Serializer):
    order_refund = serializers.BooleanField(required=False, allow_null=True)
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True, required=False)
    items = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, required=False)
    description = serializers.CharField(
        max_length=1000, required=True)

    # def validate(self, data):
    #     order_refund = data.get('order_refund', False)
    #     amount = data.get('amount', False)
    #     items = data.get('items', False)
    #
    #     if order_refund and amount and items:
    #         raise ValidationError(
    #             'you can only enter one value from order_refund, amount and items')
    #     if order_refund and amount:
    #         raise ValidationError(
    #            'you can only enter one value from order_refund, amount')
    #     if order_refund and items:
    #         raise ValidationError(
    #             'you can only enter one value from order_refund, amount and items')
    #     if amount and items:
    #         raise ValidationError(
    #             'you can only enter one value from order_refund, amount and items')
    #     if order_refund or amount or items:
    #         raise ValidationError(
    #             'you can only enter one value from order_refund, amount and items')
    #     return data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UpdateUserCardSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)

    def update(self, instance, validated_data):
        if validated_data.get('name'):
            instance.name = validated_data.get('name')
            instance.save(update_fields=['name', ])
        return instance

    def create(self, validated_data):
        pass


class ReadyOrderItemSerializer(serializers.Serializer):

    order_items = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.UserNotification
        exclude = ('user', )


class EmployeeGivePointSerializer(serializers.Serializer):
    points = serializers.IntegerField(required=True)
    phone = serializers.CharField(required=True)
    company = serializers.IntegerField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass