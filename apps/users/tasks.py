import logging
from apps.users import models as user_models
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
# from conf.celery import app
from random import randint
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.rest import Client
from django.conf import settings


# @app.task()
# def send_sms(user_id):
#     try:
#         user = user_models.User.objects.get(pk=user_id)
#         user.sms_code = randint(10000, 99999)
#         user.save(update_fields=['sms_code', ])
#         client = Client(settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
#         message = client.messages.create(to=user.phone, from_=settings.TWILIO_PHONE, body=str(user.sms_code))
#         print(str(message))
#     except Exception as e:
#         print(str(e))


# @app.task()
# def send_sms(user_id):
#     try:
#         user = user_models.User.objects.get(pk=user_id)
#         # user.sms_code = randint(10000, 99999)
#         user.sms_code = 123456
#         user.save(update_fields=['sms_code', ])
#     except Exception as e:
#         print(str(e))
