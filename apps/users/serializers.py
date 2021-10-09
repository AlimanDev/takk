from rest_framework import serializers
from apps.users import models as user_models


class UserLoginSerializer(serializers.Serializer):

    phone = serializers.CharField()
    password = serializers.CharField()


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = user_models.User
        fields = ('phone', 'password')

    def create(self, validated_data):
        phone = validated_data['phone']
        password = validated_data['password']
        instance = user_models.User.objects.create_user(phone, password)

        return instance

class VerifiedUserSerializer(serializers.Serializer):

    code = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields = [
            'username', 'date_of_birthday', 'phone',
            'avatar', 'referral_code', 'cashback', 'balance',
            'auto_fill', 'auto_fill_min_balance'
        ]
        read_only_fields = ('phone', 'referral_code', 'cashback', 'balance')


class UserPasswordChange(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserPasswordReset(serializers.Serializer):

    password = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
