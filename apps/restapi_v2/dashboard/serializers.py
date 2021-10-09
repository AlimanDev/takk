from django.db.models import Sum
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField
from rest_framework.exceptions import ValidationError
from apps.companies import models as company_models
from apps.products import models as product_models
from apps.users import models as user_models
from apps.orders import models as order_models
from apps.restapi.mobile import serializer_logics
from apps.payment import models as payment_models


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True)  # FIXME: min length 8

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields = (
            'id', 'username', 'phone', 'date_of_birthday', 'avatar',
            'referral_code'
        )
        read_only_fields = ('phone', 'id', 'referral_code')


class CafeMinSerializer(serializers.ModelSerializer):

    logo_small = serializers.ImageField()
    logo_medium = serializers.ImageField()
    logo_large = serializers.ImageField()
    created_dt = serializers.IntegerField(read_only=True, source='get_created_dt_timestamp')
    updated_dt = serializers.IntegerField(read_only=True, source='get_updated_dt_timestamp')

    class Meta:
        model = company_models.Cafe
        fields = ('id', 'logo_small', 'logo_medium', 'logo_large', 'name', 'address', 'menu', 'status',
                  'description', 'call_center', 'delivery_available', 'created_dt', 'updated_dt')


class CafeSerializer(serializers.ModelSerializer):
    logo_small = serializers.ImageField(read_only=True)
    logo_medium = serializers.ImageField(read_only=True)
    logo_large = serializers.ImageField(read_only=True)
    created_dt = serializers.IntegerField(read_only=True, source='get_created_dt_timestamp')
    updated_dt = serializers.IntegerField(read_only=True, source='get_updated_dt_timestamp')
    cafe_timezone = TimeZoneSerializerField()

    class Meta:
        model = company_models.Cafe
        fields = '__all__'  # FIXME


class CompanySerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)
    cafes = CafeMinSerializer(many=True, read_only=True)
    logo_resized = serializers.IntegerField(read_only=True)
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = company_models.Company
        fields = (
            'id', 'owner', 'is_activate', 'name', 'phone', 'email', 'ex_point',
            'validity_point_day', 'pub_show_reviews', 'pub_show_like', 'cashback_percent', 'logo',
            'logo_resized', 'loading_app_image', 'app_image_morning', 'app_image_day', 'app_image_evening',
            'exchangeable_point', 'expiration_days', 'about', 'created_dt', 'updated_dt', 'cafes'
        )


class CafeForMenu(serializers.ModelSerializer):

    class Meta:
        model = company_models.Cafe
        fields = ('id', 'name')


class MenuListSerializer(serializers.ModelSerializer):
    cafes = CafeForMenu(many=True, read_only=True)
    product_count = serializers.IntegerField(read_only=True, source='get_product_count')
    product_category_count = serializers.IntegerField(read_only=True, source='get_product_category_count')

    class Meta:
        model = company_models.Menu
        fields = ('id', 'name', 'product_count', 'product_category_count', 'cafes')


class CardSerializer(serializers.ModelSerializer):
    created_dt = serializers.IntegerField(read_only=True, source='get_created_dt_timestamp')

    class Meta:
        model = payment_models.CustomerCard
        fields = ('id', 'card_id', 'brand', 'last4', 'created_dt', 'name')


class CustomerListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    last_order_date = serializers.IntegerField(read_only=True, source='get_last_order_date')
    order_count = serializers.SerializerMethodField(read_only=True)
    orders_total_price = serializers.SerializerMethodField(read_only=True)
    os_type = serializers.CharField(read_only=True, source='get_os_type')
    free_items_count = serializers.SerializerMethodField(read_only=True)
    points = serializers.SerializerMethodField(read_only=True)
    date_joined = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = user_models.User
        fields = ('id', 'username', 'phone', 'email',
                  'cards', 'date_joined', 'order_count',
                  'orders_total_price', 'os_type', 'last_order_date',
                  'free_items_count', 'points'
                  )

    def get_order_count(self, obj) -> int:
        return obj.get_orders().count()

    def get_orders_total_price(self, obj) -> int:
        total = 0
        orders = obj.get_orders()
        if orders.exists():
            total = orders.aggregate(Sum('total_price')).get('total_price_sum')
        return total

    def get_free_items_count(self, obj) -> int:
        return obj.get_free_items(self.context.get('company')).count()

    def get_points(self, obj) -> int:
        return obj.get_company_points(self.context.get('company')).points

    def get_date_joined(self, obj):
        return int(obj.date_joined.timestamp() * 1000)


class ModifierItemSerializer(serializers.ModelSerializer):
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = product_models.ModifierItem
        fields = '__all__'


class ModifierSerializer(serializers.ModelSerializer):

    items = ModifierItemSerializer(many=True, read_only=True)
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = product_models.Modifier
        fields = '__all__'


class ProductSizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = product_models.ProductSize
        exclude = ('product', )


class ProductCategoryForProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = product_models.ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    sizes = ProductSizeSerializer(many=True)
    category = ProductCategoryForProductSerializer()
    modifiers = ModifierSerializer(many=True)
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = product_models.Product
        fields = '__all__'


class ProductCategoryCreateListSerializer(serializers.ModelSerializer):
    children = ProductCategoryForProductSerializer(many=True, read_only=True)
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = product_models.ProductCategory
        fields = '__all__'

    # def create(self, validated_data):
    #     return super().create(validated_data)


class ProductCreateSerializer(serializers.ModelSerializer):
    # sizes = ProductSizeSerializer(many=True)
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = product_models.Product
        fields = '__all__'


class ObjectSortSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    position = serializers.IntegerField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SortedSerializer(serializers.Serializer):
    obj_type = serializers.CharField(required=True)
    obj_list = ObjectSortSerializer(many=True, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
