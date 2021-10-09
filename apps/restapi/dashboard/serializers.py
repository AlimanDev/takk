from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from django.db.models import Sum
from apps.companies import models as company_models
from apps.products import models as product_models
from apps.users import models as user_models
from apps.orders import models as order_models
from apps.restapi.mobile import serializer_logics
from apps.payment import models as payment_models
from apps.users import logics as user_logics


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=50, write_only=True, required=True)
    password = serializers.CharField(
        max_length=50, write_only=True, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserPhoneVerifiedSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15, required=True)
    sms_code = serializers.IntegerField(required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CompanySerializer(serializers.ModelSerializer):
    logo_resized = serializers.ImageField()
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = company_models.Company
        exclude = ('owner', )
        extra_kwargs = {
            'is_activate': {'read_only': True}  # Это поле может изменить только владелец Такк
        }


class CafeListSerializer(serializers.ModelSerializer):
    logo_small = serializers.ImageField()
    logo_medium = serializers.ImageField()
    logo_large = serializers.ImageField()

    class Meta:
        model = company_models.Cafe
        fields = ('id', 'logo_small', 'logo_medium', 'logo_large', 'name', 'address', 'menu', 'status',
                  'description', 'call_center', 'delivery_available')


class CompanyOwnerCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(min_length=8, max_length=50, write_only=True, required=True)

    class Meta:
        model = user_models.User
        fields = ('username', 'email', 'phone', 'date_of_birthday', 'password', 'avatar')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': False},
            'phone': {'required': True},
            'date_of_birthday': {'required': False},
            'avatar': {'required': False}  # TODO не показывает в сваггере

            }

    def create(self, validated_data):
        instance = self._create_company_owner(validated_data)
        user_logics.send_sms(instance)
        return instance

    @staticmethod
    def _create_company_owner(data):
        instance = user_models.User.objects.create_user(data.get('phone'), data.get('password'))
        instance.user_type = user_models.User.COMPANY_OWNER
        instance.username = data.get('username')
        if data.get('email'):
            instance.email = data.get('email')
        if data.get('date_of_birthday'):
            instance.date_of_birthday = data.get('date_of_birthday')
        if data.get('avatar'):
            instance.avatar = data.get('avatar')
        instance.save()
        return instance


class MenuMinDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = company_models.Menu
        exclude = ('company', )


class CafePhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = company_models.CafePhoto
        exclude = ('cafe',)


class CafeWeekTimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = company_models.CafeWeekTime
        exclude = ('cafe', )


class CafeSerializer(serializers.ModelSerializer):
    menu = MenuMinDataSerializer(required=False)
    photos = CafePhotoSerializer(many=True)
    week_time = CafeWeekTimeSerializer(many=True)
    cafe_timezone = TimeZoneSerializerField()
    logo_small = serializers.ImageField(read_only=True)
    logo_medium = serializers.ImageField(read_only=True)
    logo_large = serializers.ImageField(read_only=True)
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)
    class Meta:
        model = company_models.Cafe
        exclude = ('company', )


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
    sizes = ProductSizeSerializer(many=True)
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = product_models.Product
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    created_dt = serializers.SerializerMethodField()

    class Meta:
        model = payment_models.CustomerCard
        fields = ('id', 'brand', 'last4', 'name', 'created_dt')

    def get_created_dt(self, obj):
        return int(obj.created_dt.timestamp() * 1000)


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields = ('id', 'username', 'phone',
                  'user_type', 'phone_is_verified', 'date_of_birthday',
                  'avatar',
                  )


class CompanySerializerForTakkOwnerSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer()
    cafes = CafeListSerializer(many=True)
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = company_models.Company
        exclude = ()


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    cafes = CafeListSerializer(many=True)
    created_by = UserProfileSerializer()
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)

    class Meta:
        model = company_models.Employee
        fields = '__all__'


class ProductSizeMinDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = product_models.ProductSize
        fields = ('id', 'name')


class ModifierItemMinDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = product_models.ModifierItem
        fields = ('id', 'name', 'price')


class OrderItemSerializer(serializers.ModelSerializer):

    product_size = ProductSizeMinDataSerializer()
    product_modifiers = ModifierItemMinDataSerializer(many=True)

    class Meta:
        model = order_models.OrderItem
        fields = (
            'id', 'product', 'product_size',
            'product_modifiers', 'quantity', 'product_name',
            'product_price', 'modifiers_price', 'sub_total_price',
            'total_price', 'is_free', 'free_count',
            'free_price', 'tax_percent', 'tax_rate',
        )


class OrderSerializer(serializers.ModelSerializer):

    order_items = OrderItemSerializer(many=True)
    created = serializers.IntegerField(source='get_created_timestamp')
    updated = serializers.IntegerField(source='get_updated_timestamp')

    class Meta:

        model = order_models.Order
        fields = (
            'id', 'sub_total_price', 'tax_total',
            'total_price', 'free_items', 'status',
            'pre_order_timestamp', 'tip', 'tip_percent',
            'updated', 'created', 'order_items'
        )


class OrderTransactionSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    order = OrderSerializer()
    cafe = CafeListSerializer()
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = payment_models.OrderPaymentTransaction
        fields = '__all__'


class TariffSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.BudgetTariff
        fields = '__all__'


class BudgetTransactionSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    tariff = TariffSerializer()
    created_dt = serializers.IntegerField(source='get_created_dt_timestamp', read_only=True)
    updated_dt = serializers.IntegerField(source='get_updated_dt_timestamp', read_only=True)

    class Meta:
        model = payment_models.BudgetTransaction
        fields = '__all__'


class CustomerListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    last_order_date = serializers.IntegerField(read_only=True, source='get_last_order_date', allow_null=True)
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