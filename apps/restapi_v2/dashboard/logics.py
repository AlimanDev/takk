from apps.products import models as product_models
from rest_framework.exceptions import APIException, NotFound


def get_product(product_id: int) -> product_models.Product:

    try:
        product = product_models.Product.objects.get(id=product_id)
        return product
    except product_models.Product.DoesNotExist:
        raise NotFound


def get_modifier(modifier_id: int) -> product_models.Modifier:
    try:
        modifier = product_models.Modifier.objects.get(id=modifier_id)
        return modifier
    except product_models.Modifier.DoesNotExist:
        raise NotFound


def get_modifier_item(modifier_item_id: int) -> product_models.ModifierItem:
    try:
        modifier_item = product_models.ModifierItem.objects.get(id=modifier_item_id)
        return modifier_item
    except product_models.ModifierItem.DoesNotExist:
        raise NotFound


def get_product_category(category_id: int) -> product_models.ProductCategory:
    try:
        category = product_models.ProductCategory.objects.get(id=category_id)
        return category
    except product_models.ProductCategory.DoesNotExist:
        raise NotFound