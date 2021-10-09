from apps.orders import models as order_models


def cart_items_saver(cart_items, favorite_cart):
    for item in cart_items:
        item_instance = order_models.FavoriteCartItem()
        item_instance.favorite_cart = favorite_cart
        item_instance.product = item.product
        item_instance.product_size = item.product_size
        item_instance.instruction = item.instruction
        item_instance.quantity = item.quantity
        item_instance.save()
        if item.product_modifiers.all():
            for modifier in item.product_modifiers.all():
                item_instance.product_modifiers.add(modifier)


def delivery_saver(delivery_data, user, cafe):
    delivery = None
    if delivery_data:
        delivery = order_models.Delivery()
        delivery.user = user
        delivery.instruction = delivery_data.get('instruction')
        delivery.longitude = delivery_data.get('longitude')
        delivery.latitude = delivery_data.get('latitude')
        delivery.address = delivery_data.get('address')
        delivery.price = delivery.get_delivery_price(cafe)
        delivery.save()
    return delivery


def duplicate_delivery(delivery, cafe):
    delivery_copy = order_models.Delivery()
    delivery_copy.user = delivery.user
    delivery_copy.latitude = delivery.latitude
    delivery_copy.longitude = delivery.longitude
    delivery_copy.instruction = delivery.instruction
    delivery_copy.price = delivery.get_delivery_price(cafe)
    delivery_copy.address = delivery.address
    delivery_copy.save()
    return delivery_copy
