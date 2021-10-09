import pdb
from rest_framework.exceptions import APIException, ValidationError, NotFound
from apps.companies import models as company_models
from django.http import HttpResponse
import stripe
import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.orders import models as order_models
from apps.payment import models as payment_models
from apps.users import models as user_models
from apps.restapi.mobile import serializer_logics
from apps.restapi.mobile import send_notifications
from apps.payment.logic import logics as payment_logics

##########################
# Order create logic start TODO: ну протестить и оптимизировать
##########################


def create_order(user: user_models.User,
                 cart: order_models.Cart,
                 data: dict) -> order_models.Order:
    # TODO добавить логику доставки
    order = order_models.Order()
    order.cafe = cart.cafe
    order.user = user
    order.pre_order_timestamp = data.get('pre_order_timestamp')
    order.tip = cart.tip
    order.sub_total_price = cart.get_sub_total_price()
    order.tax_total = cart.get_tax_total()
    if cart.tip_percent:
        order.tip_percent = cart.tip_percent
    if data.get('use_free_items'):  # если использовать free item
        order.free_items = cart.get_free_items_price()
        order.total_price = cart.get_total_price() - cart.get_free_items_price()
    else:
        order.total_price = cart.get_total_price()
    order.save()
    save_order_items(cart, order, data.get('use_free_items', False))
    return order


def save_order_items(cart: order_models.Cart,
                     order: order_models.Order,
                     use_free_items: bool):
    items = cart.cart_items.all()
    if use_free_items:  # Если использовать free item
        _items = items.order_by(  # для того чтобы free item использовался для самых дорогих товаров
            '-product_size__price')
        user_free_items_count = cart.get_user_free_item().count()  # количество free items пользователя
        cart_free_items_id = cart.get_cart_free_items_ids()  # id товаров которые можно обменять на free item
        for cart_item in _items:
            order_item = create_order_item(cart_item, order)
            if cart_item.id in cart_free_items_id and user_free_items_count > 0:
                if cart_item.quantity <= user_free_items_count:  # TODO: оптимизировать или перенести код
                    user_free_items_count -= cart_item.quantity
                    order_item.free_count = cart_item.quantity
                    order_item.free_price = float(cart_item.get_product_price()) * cart_item.quantity

                else:
                    order_item.free_count = user_free_items_count
                    order_item.free_price = float(cart_item.get_product_price()) * user_free_items_count
                    user_free_items_count = 0
                order_item.is_free = True
                order_item.save(update_fields=['free_count', 'free_price', 'is_free'])
    else:
        for cart_item in items:
            _ = create_order_item(cart_item, order)


def create_order_item(cart_item: order_models.CartItem,
                      order: order_models.Order) -> order_models.OrderItem:
    order_item = order_models.OrderItem.objects.create(
        order=order,
        product=cart_item.product,
        product_size=cart_item.product_size,
        quantity=cart_item.quantity,
        product_name=cart_item.product.name,
        instruction=cart_item.instruction,
        tax_percent=cart_item.get_product_tax_percent(),
        tax_rate=order.cafe.tax_rate,
        product_price=cart_item.product_size.price,
        modifiers_price=cart_item.get_modifiers_price(),
        sub_total_price=cart_item.get_product_total_price(),
        total_price=cart_item.get_total_price())

    if cart_item.product_modifiers.all():
        for mod in cart_item.product_modifiers.all():
            order_item.product_modifiers.add(mod)
    return order_item

########################
# Order create logic end
########################


def get_takk_fee(order: order_models.Order) -> int:
    """ Вернет сумму налога Такка за заказ """
    takk_fee_company = company_models.TakkFeeForCompany.objects.get(company=order.cafe.company)
    if takk_fee_company.is_percent:  # Если налог взымается в процентах
        fee = order.get_total_price_in_cents() * takk_fee_company.fee_percent / 100
    else:  # Если за каждый заказ берет определённую сумму ()
        fee = takk_fee_company.fee_amount
    return int(fee)


def order_paid(order: order_models.Order):
    order.status = order_models.Order.NEW
    order.save(update_fields=['status', ])
    send_notifications.employee_new_order(order)


def get_order(order_id) -> order_models.Order:
    order = order_models.Order.objects.get(pk=order_id)
    return order


def get_tariff(tariff_id: int) -> user_models.BudgetTariff:
    tariff = user_models.BudgetTariff.objects.get(pk=tariff_id)
    return tariff


def get_user(user_id: int) -> user_models.User:
    user = user_models.User.objects.get(pk=int(user_id))
    return user


def user_give_point(order: order_models.Order):
    user = order.user
    company = order.cafe.company
    user_points = user.get_company_points(company)
    sum_points = order.get_order_give_points() + user_points.points
    free_items_count = int(sum_points / company.exchangeable_point)
    points = sum_points - free_items_count * company.exchangeable_point
    user_points.points = points
    user_points.save(update_fields=['points', ])
    save_user_free_item(user, company, free_items_count)


def save_user_free_item(user: user_models.User,
                        company: company_models.Company, free_item_count: int):
    if free_item_count > 0:
        for i in range(0, free_item_count):
            user_models.FreeItem.objects.create(
                user=user,
                company=company
            )


def free_items_redeemed(order: order_models.Order) -> None:  # FIXME: написать коментарий
    try:
        user = order.user
        user_free_items = user.get_free_items(order.cafe.company)
        order_free_items = order.order_items.filter(is_free=True)
        i = 0
        if order_free_items:
            for order_free_item in order_free_items:
                for q in range(0, order_free_item.free_count):
                    user_free_item = user_free_items[i]
                    user_free_item.status = user_models.FreeItem.REDEEMED
                    user_free_item.product = order_free_item.product
                    user_free_item.save()
    except Exception:
        pass


def get_order_item(order_item_id: int) -> order_models.OrderItem:
    order_item = order_models.OrderItem.objects.get(pk=order_item_id)
    return order_item


def save_notification(user_id: int, title: str, body: str):
    user = get_user(user_id)
    user_models.UserNotification.objects.create(
        user=user, title=title, body=body)


def order_item_ready(order_items_ids: list):
    if order_items_ids:
        for item_id in order_items_ids:
            item = get_order_item(item_id)
            item.is_ready = True
            item.save(update_fields=['is_ready', ])


def get_company(company_id: int) -> company_models.Company:
    try:
        company = company_models.Company.objects.get(pk=company_id)
        return company
    except company_models.Company.DoesNotExist:
        raise ValidationError('Company does not exist')

