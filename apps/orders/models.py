import pdb

from django.db.models import QuerySet
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill

from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.db import models as geo_models

from apps.companies import models as company_models
from apps.users import models as user_models
from apps.products import models as product_models

import uuid


class Delivery(models.Model):
    """Адрес доставки"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='deliveries', on_delete=models.SET_NULL, null=True)
    address = models.CharField(
        max_length=255, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True)
    instruction = models.CharField(  # Инструкция доставки
        max_length=255, null=True, blank=True)
    price = models.DecimalField(  # Цена за доставку
        default=0, max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'deliveries'

    def get_distance(self, cafe):
        pnt = Point(float(self.latitude), float(self.longitude))  # Место доставки
        distance = cafe.location.distance(pnt) * 100  # Расстояние между кафе и место доставки в км
        return distance

    def get_delivery_price(self, cafe):
        distance = self.get_distance(cafe)
        price = float(cafe.delivery_fee) * float(cafe.delivery_percent) / 100.0 + float(distance) * float(
            cafe.delivery_km_amount)
        return price


class Order(models.Model):
    """ Заказ """
    WAITING = 'waiting'  # заказ еще не оплачен
    NEW = 'new'  # заказ оплачен
    READY = 'ready'  # заказ готов
    REJECT = 'refund'  # заказ отменен
    SENT_OUT = 'sent_out'  # заказ был отправлен к клиенту (если это доставка)
    DELIVERED = 'delivered'  # заказ доставлен клиенту

    ORDER_STATUS = (  # Статус заказа
        (WAITING, _('Waiting')),
        (NEW, _('New')),
        (READY, _('Ready')),
        (REJECT, _('Refund')),
        (SENT_OUT, _('Sent out')),
        (DELIVERED, _('Delivered')),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='orders', null=True, on_delete=models.SET_NULL)
    cafe = models.ForeignKey(  # К какому кафе был сделан заказ
        company_models.Cafe, null=True, on_delete=models.SET_NULL, related_name='orders')
    delivery = models.ForeignKey(  # Адрес доставки
        Delivery, blank=True, null=True, on_delete=models.SET_NULL)
    # order_unique_id = models.CharField(  # ID заказа
    #     unique=True, blank=True, null=True, max_length=120, verbose_name=_('Order Id'), editable=False)
    sub_total_price = models.DecimalField(  # Общяя сумма продуктов
        null=True, blank=True, max_digits=10, decimal_places=2)
    tax_total = models.DecimalField(  # Общяя сумма налогов
        null=True, blank=True, max_digits=10, decimal_places=2)
    total_price = models.DecimalField(  # Общяя сумма заказа
        null=True, blank=True, max_digits=10, decimal_places=2)
    free_items = models.DecimalField(  # Общяя сумма бесплатного товара
        null=True, blank=True, max_digits=10, decimal_places=2)
    status = models.CharField(  # Статус заказа
        choices=ORDER_STATUS, default=WAITING, blank=True, max_length=60)
    pre_order_timestamp = models.BigIntegerField(
        null=True, blank=True)
    tip = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2, default=0)
    tip_percent = models.IntegerField(
        null=True, blank=True, default=0)
    is_acknowledge = models.BooleanField(  # потвердил ли заказ сотрудник
        default=False)
    updated = models.DateTimeField(
        auto_now=True)
    created = models.DateTimeField(  # дата заказа
        auto_now_add=True)

    class Meta:
        db_table = 'orders'
        ordering = ('-created', )

    def get_total_price_float(self) -> float:
        return round(float(self.total_price), 2)

    def get_total_price_in_cents(self):
        return int(round(self.get_total_price_float() * 100))

    def get_created_timestamp(self):
        return self.created.timestamp() * 1000

    def get_updated_timestamp(self):
        return self.updated.timestamp() * 1000

    def get_order_give_points(self):  # вернет количество points которое получет user от заказа
        points = 0
        items = self.order_items.all()
        for item in items:
            if item.product.category.is_give_point:
                points += item.quantity
        return points

    def get_free_items(self) -> QuerySet:
        free_items = self.order_items.filter(is_free=True)
        return free_items

    def get_order_detail(self) -> str:
        order_detail = str()
        for item in self.order_items.all():
            order_detail = f"{item.product_name} x {item.quantity}, "
        return order_detail


class OrderItem(models.Model):
    """ Товар заказа """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(
        product_models.Product, on_delete=models.SET_NULL, null=True)
    product_size = models.ForeignKey(
        product_models.ProductSize, on_delete=models.SET_NULL, null=True)
    product_modifiers = models.ManyToManyField(  # Модификаторы товара
        product_models.ModifierItem, blank=True)
    quantity = models.IntegerField(
        default=1)
    product_name = models.CharField(
        max_length=150)
    product_price = models.DecimalField(  # сумма продукта
        decimal_places=2, max_digits=10, default=0)
    modifiers_price = models.DecimalField(  # Общяя сумма modifiers
        decimal_places=2, max_digits=10, default=0)
    sub_total_price = models.DecimalField(  # Общяя сумма (modifiers + product_price) * quantity
        decimal_places=2, max_digits=10, default=0)
    total_price = models.DecimalField(  # Общяя сумма sub_total_price + tax_total_price
        decimal_places=2, max_digits=10, default=0)
    instruction = models.TextField(  # инструкция (Кофе без сахара)
        null=True, blank=True)
    is_free = models.BooleanField(
        default=False)
    free_count = models.IntegerField(  # Количество бесплатного товара (заказали 5 кофе 2 из них бесплатно)
        default=0)
    free_price = models.DecimalField(
        decimal_places=2, max_digits=10, default=0)
    tax_percent = models.IntegerField(  # Процент от налового покозателя
        default=100)
    tax_rate = models.DecimalField(  # Налоговый показатель
        max_digits=100, decimal_places=3, default=0)
    is_ready = models.BooleanField(
        default=False)

    class Meta:
        db_table = 'order_items'

    def get_sub_total_price(self):
        total = (float(self.product_price) + float(self.modifiers_price)) * self.quantity
        return total

    def get_tax_price(self):
        tax = self.get_sub_total_price() * float(self.tax_rate) / 100 * self.tax_percent / 100
        return tax

    def get_total_price(self):
        total = (self.get_sub_total_price() + self.get_tax_price()) * self.quantity
        return total


class FavoriteCart(models.Model):
    """ Избранные  """
    name = models.CharField(
        max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='favorite_carts')
    cafe = models.ForeignKey(
        company_models.Cafe, on_delete=models.CASCADE, null=True)
    delivery = models.ForeignKey(
        Delivery, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'favorite_carts'

    def get_sub_total_price(self):  # Общая сумма товаров
        total = 0
        items = self.favorite_cart_items.all()
        if items:
            for item in items:
                total += item.get_product_total_price()
        return total


class FavoriteCartItem(models.Model):
    """ Избранные товары """
    favorite_cart = models.ForeignKey(
        FavoriteCart, on_delete=models.CASCADE, related_name='favorite_cart_items')
    product = models.ForeignKey(
        product_models.Product, on_delete=models.CASCADE)
    product_size = models.ForeignKey(
        product_models.ProductSize, on_delete=models.SET_NULL, null=True)
    product_modifiers = models.ManyToManyField(
        product_models.ModifierItem, blank=True)
    instruction = models.TextField(  # инструкция (Кофе без сахара)
        null=True, blank=True)
    quantity = models.IntegerField(
        default=1)

    class Meta:
        db_table = 'favorite_cart_items'

    def get_product_price(self):
        product_price = self.product_size.price
        return float(product_price)

    def get_modifiers_price(self):
        modifiers_price = 0
        if self.product_modifiers:
            for item in self.product_modifiers.all():
                modifiers_price += item.price
        return float(modifiers_price)

    def get_product_total_price(self):
        product_price = self.get_product_price()
        modifiers_price = self.get_modifiers_price()
        total = (product_price + modifiers_price) * self.quantity
        return total


class Cart(models.Model):
    """ Корзина  """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='cart')
    cafe = models.ForeignKey(
        company_models.Cafe, on_delete=models.CASCADE, null=True, related_name='cafes')
    tip = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2, default=0)
    tip_percent = models.IntegerField(
        null=True, blank=True, default=0)

    class Meta:
        db_table = 'carts'

    def get_sub_total_price(self) -> float:  # Общая сумма товаров
        total = 0.
        items = self.cart_items.all()
        if items.exists():
            for item in items:
                total += item.get_product_total_price()
        return round(total, 2)

    def get_tax_total(self) -> float:  # Общая сумма налога
        total = 0.
        items = self.cart_items.all()
        if items.exists():
            for item in items:
                total += item.get_product_total_tax_price()
        return round(total, 2)

    def get_user_free_item(self) -> QuerySet:
        user = self.user
        free_items = user.get_free_items(self.cafe.company)
        return free_items

    def get_free_items_price(self) -> float:  # Общая сумма бесплатных товаров

        total = float()
        cart_items = self.cart_items.all().order_by('-product_size__price')  # чтоб исп freeitem на самые дорогие товары
        if cart_items:
            free_items_count = self.get_user_free_item().count()
            cart_free_items_id = self.get_cart_free_items_ids()  # id товаров корзины которые можно обменять на free item

            if free_items_count > 0 and cart_free_items_id:
                for cart_item in cart_items:
                    if cart_item.id in cart_free_items_id and free_items_count > 0:
                        if cart_item.quantity <= free_items_count:
                            total += float(cart_item.product_size.price) * cart_item.quantity
                            free_items_count -= cart_item.quantity
                        else:
                            total += float(cart_item.product_size.price) * free_items_count
                            free_items_count = 0
        return round(total, 2)

    def get_total_price(self) -> float:
        sub_total_price = self.get_sub_total_price()
        total_tax = self.get_tax_total()
        total = sub_total_price + total_tax + float(self.tip)
        return round(total, 2)

    def get_cart_free_items_ids(self) -> list:
        cart_items = self.cart_items.all()
        cart_free_item_ids = []
        for cart_item in cart_items:
            if cart_item.product.category.is_exchange_free_item:
                cart_free_item_ids.append(cart_item.id)
        return cart_free_item_ids

    def empty_cart(self):
        self.cart_items.all().delete()
        self.cafe = None
        self.tip = 0
        self.tip_percent = 0
        self.save()

    def is_cart_valid(self) -> bool:
        if self.cafe and self.cart_items.exists():
            return True
        return False

    def create_cart_items(self, items):
        self.empty_cart()

        for item in items:
            if item.product and item.product_size:
                cart_item = CartItem.objects.create(
                    cart=self,
                    product=item.product,
                    product_size=item.product_size,
                    instruction=item.instruction,
                    quantity=item.quantity,
                )
                if item.product_modifiers.all():
                    for mod in item.product_modifiers.all():
                        cart_item.product_modifiers.add(mod)

    def get_total_price_with_free_items(self):
        free_items_price = self.get_free_items_price()
        total_price = self.get_total_price()
        return total_price - free_items_price

    def get_cafe_products_tax(self):  # Налоговый показатель для продуктов

        items = self.cart_items.all()
        if items:
            tax_rate = float(self.cafe.tax_rate)
            all_tax_50 = True
            all_tax_0 = True
            for item in items:
                tax_percent = item.get_product_tax_percent()
                if tax_percent == 0:
                    all_tax_50 = False
                if tax_percent == 50:
                    all_tax_0 = False
                if tax_percent == 100:
                    all_tax_0 = False
                    all_tax_50 = False
            if all_tax_0:
                return 0
            if all_tax_50:
                return round(tax_rate / 2, 3)
            return tax_rate
        return 0


class CartItem(models.Model):
    """ Товары корзины """
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(
        product_models.Product, on_delete=models.CASCADE)
    product_size = models.ForeignKey(
        product_models.ProductSize, on_delete=models.SET_NULL, null=True)
    product_modifiers = models.ManyToManyField(
        product_models.ModifierItem, blank=True)
    instruction = models.TextField(  # инструкция (Кофе без сахара)
        null=True, blank=True)
    quantity = models.IntegerField(
        default=1)

    class Meta:
        db_table = 'cart_items'

    def get_product_price(self) -> float:  # сумма самого продукта
        product_price = self.product_size.price
        return float(product_price)

    def get_modifiers_price(self) -> float:  # общяя сумма modifiers продукта
        modifiers_price = 0.
        if self.product_modifiers.exists():
            for item in self.product_modifiers.all():
                modifiers_price += float(item.price)
        return round(float(modifiers_price) * self.quantity, 2)

    def get_product_total_price(self) -> float:  # обшяя сумма (product + modifier) * quantity
        product_price = self.get_product_price()
        modifiers_price = self.get_modifiers_price()
        total = product_price * self.quantity + modifiers_price
        return round(total, 2)

    def get_product_total_tax_price(self) -> float:  # обший налог продукта
        product_total_price = self.get_product_total_price()
        tax = self.get_product_tax_percent()
        cafe_tax = float(self.cart.cafe.tax_rate)
        product_tax = product_total_price * (cafe_tax / 100) * (tax / 100)
        return round(product_tax, 2)

    def get_product_tax_percent(self) -> int:  # налог продукта
        return self.product.tax_percent

    def get_total_price(self) -> float:
        sub_total_price = self.get_product_total_price()
        tax_total = self.get_product_total_tax_price()
        total = sub_total_price + tax_total
        return total

