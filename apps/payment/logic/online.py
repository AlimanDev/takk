import pdb

from apps.companies import models as company_models
from apps.payment import models as payment_models
from apps.restapi.mobile import client_views_logic
from apps.restapi_v2.mobile import logics as mobile_logics
from apps.orders.models import Order
from apps.payment.logic import logics as payment_logics
from apps.users import models as user_models


def save_online_order_transaction(payment_intent) -> None:
    try:
        order = mobile_logics.get_order(payment_intent.get('metadata').get('order_id'))
        card_detail = payment_logics.get_card_detail(payment_intent.charges.data[0])
        payment_models.OrderPaymentTransaction.objects.create(
            customer=order.user,
            cafe=order.cafe,
            order=order,
            amount=order.get_total_price_float(),
            takk_fee=payment_logics.get_takk_fee(order.get_total_price_float(), order.cafe),
            stripe_fee=payment_logics.get_stripe_fee(order.get_total_price_float()),
            order_detail=order.get_order_detail(),
            brand=card_detail.get('brand', ''),
            last4=card_detail.get('last4', ''),
            payment_id=payment_intent.get('id'),
            payment_type=payment_models.OrderPaymentTransaction.ONLINE,
            is_capture=False,
        )
        mobile_logics.order_paid(order)
        mobile_logics.free_items_redeemed(order)
        mobile_logics.user_give_point(order)

    except Exception as e:
        print(e)  # TODO: добавить логирование




