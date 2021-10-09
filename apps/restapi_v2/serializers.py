
from rest_framework import serializers

from apps.companies import models as company_models
from apps.orders import models as order_models
from apps.products import models as product_models
from apps.payment import models as payment_models
from apps.users import models as user_models


class CompanySerializer(serializers.ModelSerializer):
    created_dt = serializers.IntegerField(read_only=True, source='get_created_dt_timestamp')
    updated_dt = serializers.IntegerField(read_only=True, source='get_updated_dt_timestamp')
    logo_resized = serializers.ImageField(read_only=True)

    class Meta:
        model = company_models.Company
        fields = (
            'id', 'name', 'phone', 'email',
            'ex_point', 'validity_point_day', 'cashback_percent',
            'logo', 'logo_resized', 'loading_app_image', 'app_image_morning',
            'app_image_day', 'app_image_evening', 'exchangeable_point',
            'expiration_days', 'about', 'created_dt', 'updated_dt')


class CompanyMinDataSerializer(serializers.ModelSerializer):
    created_dt = serializers.IntegerField(read_only=True, source='get_created_dt_timestamp')
    updated_dt = serializers.IntegerField(read_only=True, source='get_updated_dt_timestamp')
    logo_resized = serializers.ImageField(read_only=True)

    class Meta:
        model = company_models.Company
        fields = (
            'id', 'name', 'phone', 'email',
            'logo', 'logo_resized', 'about',
            'created_dt', 'updated_dt')


class TariffSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.BudgetTariff
        fields = ('id', 'amount_payout', 'amount_receipt')
