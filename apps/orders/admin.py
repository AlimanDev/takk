from django.contrib import admin
from apps.orders import models as order_models


@admin.register(order_models.Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(order_models.Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    pass


@admin.register(order_models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(order_models.FavoriteCart)
class FavoriteCartAdmin(admin.ModelAdmin):
    pass


@admin.register(order_models.FavoriteCartItem)
class FavoriteCartItemAdmin(admin.ModelAdmin):
    pass


@admin.register(order_models.Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(order_models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass



