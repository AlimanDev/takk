from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField
from apps.companies import models as company_models
from apps.products import models as product_models
from apps.users import models as user_models
from apps.orders import models as order_models
from apps.payment import models as payment_models


class ProductCategorySerializer(serializers.ModelSerializer):
    image_small = serializers.ImageField()
    image_medium = serializers.ImageField()
    image_large = serializers.ImageField()
    start = serializers.TimeField(source='get_start_time')
    end = serializers.TimeField(source='get_end_time')

    class Meta:
        model = product_models.ProductCategory
        exclude = ('is_give_point', 'is_exchange_free_item')


class ProductCategoryCheckDataSerializer(serializers.Serializer):
    categories = ProductCategorySerializer(many=True, read_only=True)
    server_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductCategoryCheckSerializer(serializers.Serializer):
    update_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=True, write_only=True)
    message = serializers.CharField(max_length=250, read_only=True)
    status = serializers.IntegerField(read_only=True)
    # data = serializers.SerializerMethodField()
    data = ProductCategoryCheckDataSerializer(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductSubCategoryCheckDataSerializer(serializers.Serializer):

    sub_categories = ProductCategorySerializer(many=True, read_only=True)
    server_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductSubCategoryCheckSerializer(serializers.Serializer):

    update_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=True, write_only=True)
    message = serializers.CharField(max_length=250, read_only=True)
    status = serializers.IntegerField(read_only=True)
    data = ProductSubCategoryCheckDataSerializer(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = product_models.ProductSize
        fields = '__all__'


class ProductModifierItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = product_models.ModifierItem
        fields = '__all__'


class ProductModifierSerializer(serializers.ModelSerializer):

    # items = ProductModifierItemSerializer(many=True)

    class Meta:
        model = product_models.Modifier
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    image_small = serializers.ImageField()
    image_medium = serializers.ImageField()
    image_large = serializers.ImageField()
    sub_category = serializers.IntegerField(source='get_sub_category_id')
    category = serializers.IntegerField(source='get_category_id')
    sizes = serializers.ListField(child=serializers.IntegerField(), source='get_size_ids')
    # modifiers = ProductModifierSerializer(many=True, read_only=True)
    start = serializers.TimeField(source='get_start_time')
    end = serializers.TimeField(source='get_end_time')

    class Meta:
        model = product_models.Product
        fields = '__all__'


class ProductCheckDataSerializer(serializers.Serializer):
    products = ProductSerializer(many=True, read_only=True)
    server_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductCheckSerializer(serializers.Serializer):

    update_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=True, write_only=True)
    message = serializers.CharField(max_length=250, read_only=True)
    status = serializers.IntegerField(read_only=True)
    data = ProductCheckDataSerializer(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductModifierCheckDataSerializer(serializers.Serializer):

    modifiers = ProductModifierSerializer(many=True, read_only=True)
    server_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductModifierCheckSerializer(serializers.Serializer):

    update_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=True, write_only=True)
    message = serializers.CharField(max_length=250, read_only=True)
    status = serializers.IntegerField(read_only=True)
    data = ProductModifierCheckDataSerializer(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductModifierItemCheckDataSerializer(serializers.Serializer):

    modifier_items = ProductModifierItemSerializer(many=True, read_only=True)
    server_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductModifierItemCheckSerializer(serializers.Serializer):

    update_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=True, write_only=True)
    message = serializers.CharField(max_length=250, read_only=True)
    status = serializers.IntegerField(read_only=True)
    data = ProductModifierItemCheckDataSerializer(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductSizeCheckDataSerializer(serializers.Serializer):

    sizes = ProductSizeSerializer(many=True, read_only=True)
    server_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ProductSizeCheckSerializer(serializers.Serializer):

    update_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=True, write_only=True)
    message = serializers.CharField(max_length=250, read_only=True)
    status = serializers.IntegerField(read_only=True)
    data = ProductSizeCheckDataSerializer(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class OrderItemSerializer(serializers.ModelSerializer):
    tax_total = serializers.DecimalField(
        decimal_places=2, max_digits=10, read_only=True, source='get_tax_price')

    class Meta:
        model = order_models.OrderItem
        exclude = ('order', 'is_free', 'free_count', 'free_price', 'is_ready')
        extra_kwargs = {
            'product': {'required': True},
            'product_size': {'required': True},
            'quantity': {'required': True},
            'product_modifiers': {'required': False},
            'product_name': {'read_only': True},
            'product_price': {'read_only': True},
            'modifiers_price': {'read_only': True},
            'sub_total_price': {'read_only': True},
            'total_price': {'read_only': True},
            'instruction': {'required': False},
            'tax_percent': {'read_only': True},
            'tax_rate': {'read_only': True},
        }

    def create(self, validated_data):
        pass


class OrderSerializer(serializers.ModelSerializer):

    products = OrderItemSerializer(many=True, required=True, source='order_items')
    tip_percentage = serializers.IntegerField(  # не менять название поля
        source='tip_percent', required=False)
    tip_custom_amount = serializers.DecimalField(  # не менять название поля
        max_digits=10, decimal_places=2, source='tip', required=False)

    class Meta:
        model = order_models.Order
        exclude = ('user', 'delivery',  'free_items', 'pre_order_timestamp',
                   'tip_percent', 'tip',
                   )
        extra_kwargs = {
            'sub_total_price': {'read_only': True},
            'tax_total': {'read_only': True},
            'total_price': {'read_only': True},
            'status': {'read_only': True},
            'is_confirm': {'read_only': True},
            'cafe': {'required': True},
            # 'is_ready': {'read_only': True}
        }

    def create(self, validated_data):
        # import pdb;
        # pdb.set_trace()

        instance = order_models.Order()
        instance.cafe = validated_data.get('cafe')
        if validated_data.get('tip'):
            instance.tip = validated_data.get('tip')
        elif validated_data.get('tip_percent'):
            instance.tip_percent = validated_data.get('tip_percent')
        instance.save()
        self.order_item_saver(validated_data.get('order_items'), instance)
        return instance

    @staticmethod
    def order_item_saver(items, order):
        sub_total_price = 0
        tax_total_price = 0

        for item in items:

            order_item = order_models.OrderItem()
            order_item.order = order
            order_item.product = item.get('product')
            order_item.product_size = item.get('product_size')
            order_item.quantity = item.get('quantity')
            order_item.product_name = order_item.product.name
            order_item.product_price = order_item.product_size.price
            order_item.tax_percent = order_item.product.tax_percent
            order_item.tax_rate = order.cafe.tax_rate
            if item.get('instruction'):
                order_item.instruction = item.get('instruction')
            order_item.save()

            if item.get('product_modifiers'):
                for mod in item.get('product_modifiers'):
                    order_item.product_modifiers.add(mod)
                    order_item.modifiers_price = float(order_item.modifiers_price) + float(mod.price)

            order_item.sub_total_price = order_item.get_sub_total_price()
            order_item.total_price = order_item.get_total_price()
            sub_total_price += order_item.get_sub_total_price()
            tax_total_price += order_item.get_tax_price()
            order_item.save(update_fields=['sub_total_price', 'total_price', 'modifiers_price'])

        order.sub_total_price = sub_total_price
        order.tax_total = tax_total_price
        tip = 0
        if order.tip_percent > 0:
            tip = (sub_total_price + tax_total_price) * order.tip_percent / 100
            order.tip = tip
        elif order.tip > 0:
            tip = float(order.tip)

        order.total_price = sub_total_price + tax_total_price + tip
        order.save(update_fields=['sub_total_price', 'tax_total', 'total_price'])


class FinishOrderPaymentSerializer(serializers.Serializer):
    payment_id = serializers.CharField(max_length=250)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
