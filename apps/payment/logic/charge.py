import stripe
from apps.payment import models as payment_models
from rest_framework.response import Response
from apps.orders import models as order_models
from apps.companies import models as company_models
from django.conf import settings
from rest_framework.exceptions import NotFound, APIException
from apps.users import models as user_models
from apps.payment.logic import logics as payment_logics
from apps.restapi_v2.mobile import logics as mobile_logics


def save_card_order_transaction(payment_intent: dict) -> None:
    order = mobile_logics.get_order(payment_intent.get('metadata').get('order_id'))
    card = mobile_logics.get_user_card(payment_intent.get('metadata').get('card_id'))
    card_detail = {
        'payment_intent_id': payment_intent.get('id'),
        'card': card
    }
    create_card_transactions(order.user, order, card_detail, False)


def create_card_transactions(user: user_models.User, order: order_models.Order,
                             card_detail: dict, is_charge: bool):
    card = card_detail.get('card')
    if is_charge:
        payment_type = payment_models.OrderPaymentTransaction.CARD_CHARGE
    else:
        payment_type = payment_models.OrderPaymentTransaction.CARD

    payment_models.OrderPaymentTransaction.objects.create(
        payment_type=payment_type,
        payment_id=card_detail.get('payment_intent_id'),
        card=card,
        customer=user,
        order=order,
        order_detail=order.get_order_detail(),
        cafe=order.cafe,
        last4=card.last4,
        brand=card.brand,
        amount=order.get_total_price_float(),
        takk_fee=payment_logics.get_takk_fee(order.get_total_price_float(), order.cafe),
        stripe_fee=payment_logics.get_stripe_fee(order.get_total_price_float()),
        is_capture=False
    )
    mobile_logics.order_paid(order)
    mobile_logics.free_items_redeemed(order)
    mobile_logics.user_give_point(order)


def create_payment_intent_and_confirm_off_session(customer: payment_models.StripeCustomer,
                                                  card: payment_models.CustomerCard,
                                                  order: order_models.Order) -> dict:
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payment_intent = stripe.PaymentIntent.create(
            amount=order.get_total_price_in_cents(),
            currency='usd',
            payment_method_types=["card"],
            customer=customer.customer_id,
            payment_method=card.card_id,
            capture_method='manual',
            off_session=True,
            confirm=True,
            metadata={
                'payment_type': 'card_charge_confirm',
                'order_id': order.id,
                'user_id': customer.user_id,
                'card_id': card.id
            }
        )
        if payment_intent.status == 'requires_capture':
            card_detail = {
                'payment_intent_id': payment_intent.id,
                'card': card
            }
            create_card_transactions(customer.user, order, card_detail, customer.is_verified)
        return {
            'payment_type': 'card',
            'payment_status': 'paid',
            'client_secret': None,
            'cashback': 0
        }

    except stripe.error.CardError as e:
        if e.code == 'authentication_required':
            card.is_confirm_off_session = False
            card.save(update_fields=['is_confirm_off_session', ])
            return create_payment_intent_and_confirm_on_session(customer, card, order)
        raise APIException(str(e))
    except Exception as e:
        print('6')
        raise APIException(str(e))


def create_payment_intent_and_confirm_on_session(customer: payment_models.StripeCustomer,
                                                 card: payment_models.CustomerCard,
                                                 order: order_models.Order) -> dict:
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payment_intent = stripe.PaymentIntent.create(
            amount=order.get_total_price_in_cents(),
            currency='usd',
            payment_method_types=["card"],
            customer=customer.customer_id,
            payment_method=card.card_id,
            capture_method='manual',
            off_session=False,
            confirm=False,
            metadata={
                'payment_type': 'card',
                'order_id': order.id,
                'user_id': customer.user_id,
                'card_id': card.id
            }
        )
        return {
            'payment_type': 'card',
            'payment_status': 'required_confirm',
            'client_secret': payment_intent.client_secret,
            'cashback': 0
        }

    except Exception as e:
        raise APIException(str(e))
