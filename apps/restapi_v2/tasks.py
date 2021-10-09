from conf.celery import app
from twilio.rest import Client
from django.conf import settings
from apps.restapi_v2.mobile import logics as mobile_logics

from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice


@app.task()
def send_sms(phone: str, message: str) -> None:
    try:
        client = Client(settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
        client.messages.create(to=phone, from_=settings.TWILIO_PHONE, body=message)
    except Exception as e:
        print(str(e))  # TODO: добавить логирование


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
