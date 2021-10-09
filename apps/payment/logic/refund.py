from apps.payment import models as payment_models
from rest_framework.exceptions import NotFound, APIException
from apps.orders import models as order_models
from rest_framework.response import Response
from rest_framework import status
from apps.restapi import exceptions as my_exceptions


def get_transaction(order):
    try:
        transaction = payment_models.OrderPaymentTransaction.objects.get(order=order)
        return transaction
    except payment_models.OrderPaymentTransaction.DoesNotExist:
        raise NotFound('does not order transaction')


def refund_amount_to_user_balance(refund_data):
    user = refund_data.get('transaction').user
    refund_amount = refund_data.get('refund_amount')
    user_balance = float(user.balance)
    user.balance = refund_amount + user_balance
    user.save(update_fields=['balance', ])


def make_order_status_refund(order):
    order.status = order_models.Order.REJECT
    order.save(update_fields=['status', ])


def save_refund_balance_payment(refund_data):
    transaction = refund_data.get('transaction')
    transaction.status = payment_models.OrderPaymentTransaction.REFUND
    transaction.employee = refund_data.get('employee')
    transaction.refund_amount = int(refund_data.get('refund_amount') * 100)
    transaction.refund_description = refund_data.get('description')
    transaction.save()
    if refund_data.get('items'):
        order_items = transaction.order.order_items.all()
        for item_id in refund_data.get('items'):
            item = order_items.get(pk=item_id)
            transaction.refund_order_items.add(item)


def get_refund_data(transaction, employee, order, data):  # вернет dict с данными для сохранения refund
    refund_amount = 0

    refund_data = {
        'order': order,
        'transaction': transaction,
        'employee': employee,
        'description': data.get('description', '')
    }

    if data.get('order_refund'):  # Возврат суммы заказа
        refund_amount = float(transaction.amount - transaction.cashback) / 100
    elif data.get('amount'):  # Возврат определенной суммы amount
        refund_amount = float(data.get('amount'))
        if refund_amount > transaction.get_amount_in_float():  # если сумма возврата больше суммы заказа
            raise my_exceptions.RefundAmountInvalid
    elif data.get('items'):  # возварт товаров заказа

        order_items = order.order_items.all()
        for item_id in data.get('items'):
            try:
                item = order_items.get(pk=item_id)
                if item.is_free:
                    raise my_exceptions.RefundInvalidItem
                refund_amount += item.total_price
            except Exception as e:
                raise my_exceptions.RefundInvalidItem
        refund_data['items'] = data.get('items', None)
    refund_data['refund_amount'] = refund_amount
    return refund_data


def save_refund_online_payment(refund_data, refund_id=None):
    transaction = refund_data.get('transaction')
    transaction.status = payment_models.OrderPaymentTransaction.REFUND
    transaction.employee = refund_data.get('employee')
    transaction.refund_amount = int(refund_data.get('refund_amount') * 100)
    transaction.refund_description = refund_data.get('description')
    transaction.is_capture = True
    if refund_id:
        transaction.refund_id = refund_id
    transaction.save()
    if refund_data.get('items'):
        order_items = transaction.order.order_items.all()
        for item_id in refund_data.get('items'):
            item = order_items.get(pk=item_id)
            transaction.refund_order_items.add(item)
