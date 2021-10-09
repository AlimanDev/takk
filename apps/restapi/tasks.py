import datetime
from apps.users import models as user_models
from apps.restapi.mobile import client_views_logic as mobile_logics
import stripe
from django.conf import settings
from conf.celery import app
from apps.payment import models as payment_models
import random
from twilio.rest import Client
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from apps.orders import models as order_models
from apps.restapi.mobile import send_notifications


@app.task
def send_sms(user_id):
    try:
        user = user_models.User.objects.get(id=user_id)
        if user:
            user.sms_code = random.randint(10000, 99999)
            user.sms_code = 123456
            user.save(update_fields=['sms_code', ])
            client = Client(settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
            message = client.messages.create(
                body='Your code - {}'.format(user.sms_code),
                from_=settings.TWILIO_PHONE,
                to='+998999646564'  # для теста
                # to=user.phone
            )
            print(str(message))
    except Exception as e:
        print(str(e))


@app.task
def send_notification(user_id: int, title: str, body: str):
    try:
        message = Message(
            notification=Notification(title=title, body=body))
        devices = FCMDevice.objects.filter(user__id=user_id, active=True).first()
        devices.send_message(message)
        mobile_logics.save_notification(user_id, title, body)
    except Exception as e:
        print(e)
