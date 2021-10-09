from apps.companies import models as company_models
from rest_framework import serializers
from apps.users import serializers as user_serializers

#
# class CompanyForUser(serializers.ModelSerializer):
#
#     class Meta:
#         model = company_models.Company
#         fields = ('id', 'name', 'logo')
#
#
# class CafeForUserSerializer(serializers.ModelSerializer):
#     company = CompanyForUser()
#
#     class Meta:
#         model = company_models.Cafe
#         exclude = ('order_limit', 'order_time_limit', 'is_activate')
