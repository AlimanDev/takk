from random import randint
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.rest import Client
from django.conf import settings
from apps.users import models as user_models

# def send_sms(user):
#     try:
#         user.sms_code = randint(10000, 99999)
#         user.save(update_fields=['sms_code', ])
#         client = Client(settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
#         message = client.messages.create(to=user.phone, from_=settings.TWILIO_PHONE, body=str(user.sms_code))
#         print(str(message))
#     except Exception as e:
#         print(str(e))


def send_sms(user):
    # TODO: Дописать логику отправки смс
    # user.sms_code = randint(10000, 99999)
    user.sms_code = 123456
    user.save(update_fields=['sms_code', ])


def get_tokens_for_user(user: user_models.User) -> dict:

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
