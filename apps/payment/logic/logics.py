import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import pdb
import stripe
import json

from rest_framework.exceptions import NotFound, APIException
from apps.payment import models as payment_models
from apps.orders import models as order_models
from apps.companies import models as company_models
from apps.users import models as user_models
from django.conf import settings
from apps.restapi.mobile import client_views_logic
from apps.payment.logic import balance as balance_logics
from apps.payment.logic import online as online_logics
from apps.payment.logic import charge as card_logics


def processing_event(event):
    if check_event_created(event):  # если event еще не был обработан
        payment_type = event.data.object.metadata.get('payment_type')

        if event.type == 'payment_intent.amount_capturable_updated':  # Если деньги были успешно заморажены
            if payment_type == 'online':  # онлайн оплата заказа
                online_logics.save_online_order_transaction(event.data.object)
            if payment_type == 'card':
                card_logics.save_card_order_transaction(event.data.object)
        if event.type == 'payment_method.attached':
            save_new_card_customer(event.data.object)


def save_new_card_customer(data: dict) -> None:
    try:
        customer = payment_models.StripeCustomer.objects.get(customer_id=data.get('customer'))
        payment_method = data.get('id')
        card_data = data.get('card')
        name = f'Card {card_data.get("brand")} ***{card_data.get("last4")}'
        new_card, _ = payment_models.CustomerCard.objects.update_or_create(
            user=customer.user, brand=card_data.get('brand'), last4=card_data.get('last4'),
            defaults={'card_id': payment_method, 'name': name}
        )
    except Exception as e:
        pass  # TODO: добавить в логировании


def check_event_created(event) -> bool:
    """STRIPE отправляет один и тот же event несколько раз
        чтобы не обрабатывать один и тот же event сохраняем event_id
    """
    event_instance, created = payment_models.StripeWebhookEvent.objects.get_or_create(event_id=event.get('id'))
    if created:
        return True
    else:
        event_instance.count += 1
        event_instance.save(update_fields=['count', ])
        return False


def get_card(card_id: int) -> payment_models.CustomerCard:
    """Вернет сохраненную катру пользователя"""
    try:
        card = payment_models.CustomerCard.objects.get(pk=card_id)
        return card
    except payment_models.CustomerCard.DoesNotExist:
        raise NotFound('card does not exist')


def get_stripe_fee(amount: float):
    fee = amount * 0.029 + 0.3
    return round(fee, 2)


def get_takk_fee(amount: float, cafe: company_models.Cafe) -> float:  # FIXME дописать логику
    return float(0.5)


def get_stripe_customer(user: user_models.User) -> payment_models.StripeCustomer:
    try:
        customer, created = payment_models.StripeCustomer.objects.get_or_create(user=user)
        if created:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_customer = stripe.Customer.create(
                name=user.get_customer_name(), phone=user.phone)
            customer.customer_id = stripe_customer.get('id')
            customer.save(update_fields=['customer_id', ])
            return customer
        else:
            return customer
    except Exception as e:
        raise APIException(str(e))


def get_card_detail(data: dict) -> dict:  # извлекает данные карты чтобы сохранить в OrderPaymentTransaction
    payment_method = data.get('payment_method')
    payment_method_details = data.get('payment_method_details')
    brand = payment_method_details.get('card').get('brand')
    last4 = payment_method_details.get('card').get('last4')
    return {
        'payment_method': payment_method,
        'brand': brand,
        'last4': last4
    }
