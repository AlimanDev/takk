import stripe
from rest_framework.exceptions import ValidationError, APIException
from django.conf import settings
from apps.users import models as user_models
from apps.orders import models as order_models
from apps.payment import models as payment_models
from apps.restapi.mobile import client_views_logic
from apps.companies import models as company_models
from apps.payment.logic import logics as payment_logics


def pay_user_balance(user: user_models.User, order: order_models.Order) -> float:
    cashback_percent = company_models.TakkGeneralSettings.load().cashback
    cashback = round(order.get_total_price_float() * cashback_percent / 100, 2)

    user_balance = user.get_balance_float()
    user.balance = round(user_balance - order.get_total_price_float() + cashback, 2)
    user.save(update_fields=['balance', ])

    user_models.CashbackHistory(
        user=user,
        order=order,
        amount=cashback,
        )
    return cashback


def save_order_transaction(
        user: user_models.User, order: order_models.Order, cashback: float) -> None:

    payment_models.OrderPaymentTransaction.objects.create(
        customer=user,
        order=order,
        order_detail=order.get_order_detail(),
        cafe=order.cafe,
        amount=order.get_total_price_float(),
        takk_fee=payment_logics.get_takk_fee(order.get_total_price_float(), order.cafe),
        stripe_fee=get_stripe_fee_for_balance(order.get_total_price_float()),
        customer_cashback=cashback,
        payment_type=payment_models.OrderPaymentTransaction.BALANCE,
    )


def top_up_balance_online(user: user_models.User,
                          tariff: user_models.BudgetTariff) -> dict:
    """ Вернет client_secret для того чтобы завершить платеж на мобильной стороне
        после оплаты stripe отправит данные о платеже через webhook
    """
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payment_intent = stripe.PaymentIntent.create(
            amount=tariff.get_amount_payout_in_cents(),
            currency="usd",
            payment_method_types=["card"],
            metadata={
                'type': 'tariff_online',
                'user_id': user.id,
                'tariff_id': tariff.id
            }
        )
        return {'client_secret': payment_intent.client_secret}
    except Exception as e:
        raise ValidationError(str(e))


def top_up_balance_online_finish(payment_intent):
    # Это обрабатывает данные которые приходят через stripe webhook
    tariff_id = payment_intent.get('metadata').get('tariff_id')
    user_id = payment_intent.get('metadata').get('user_id')
    tariff = client_views_logic.get_tariff(tariff_id)
    user = client_views_logic.get_user(user_id)
    create_budget_transaction_and_update_balance(user, tariff, payment_intent.get('id'))


def top_up_balance_with_card(user: user_models.User,
                             tariff: user_models.BudgetTariff, card_id: int) -> dict:
    try:
        card = payment_logics.get_card(card_id)
        response_data = dict()
        customer_id = user.stripe_customer.customer_id
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payment_intent = stripe.PaymentIntent.create(
            amount=tariff.get_amount_payout_in_cents(),
            currency='usd',
            customer=customer_id,
            payment_method=card.card_id,
            confirm=True,
            off_session=True,
            metadata={
                'type': 'tariff_card',
                'tariff_id': tariff.id,
                'card_id': card.id,
                'user_id': user.id
            }
        )
        if payment_intent.status == 'succeeded':
            response_data['detail'] = 'paid'
            create_budget_transaction_and_update_balance(user, tariff, payment_intent.id)
        else:
            response_data['detail'] = 'Error'
        return response_data
    except Exception as e:
        raise APIException(str(e))


def create_budget_transaction_and_update_balance(user: user_models.User,
                                                 tariff: user_models.BudgetTariff, payment_id: str):
    # Это функция сохраняет транзакцию, обновляет баланс пользователя и сохраняет историю пополнения пользователя
    transaction = payment_models.BudgetTransaction.objects.create(
        user=user,
        payment_id=payment_id,
        tariff=tariff,
        amount_payout=tariff.get_amount_payout_in_cents(),
        amount_receipt=tariff.get_amount_receipt_in_cents()
    )
    user_update_balance = float(user.get_balance_in_cents() + transaction.amount_receipt) / 100
    user.balance = user_update_balance
    user.save(update_fields=['balance', ])

    user_models.BudgetFillHistory.objects.create(
        user=user,
        tariff=tariff,
        amount_payout=tariff.amount_payout,
        amount_receipt=tariff.amount_receipt,
        transaction=transaction,
    )


def get_stripe_fee_for_balance(amount: float):

    fee = amount * 0.029 + 0.20
    return fee



