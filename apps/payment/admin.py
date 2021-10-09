from django.contrib import admin
from apps.payment import models as payment_models


@admin.register(payment_models.OrderPaymentTransaction)
class OrderPaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'status', 'payment_type', 'is_capture', 'created_dt', 'updated_dt')
    search_fields = ('customer__id', 'order__id', 'id', 'final_transaction__id')
    list_filter = ('status', 'is_capture', 'created_dt', 'payment_type')


@admin.register(payment_models.BudgetTransaction)
class BudgetTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tariff', 'amount_payout', 'created_dt')
    search_fields = ('user__id', 'order__id', 'id', 'final_transaction__id')
    list_filter = ('created_dt', )


@admin.register(payment_models.StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'customer_id', 'created_dt', 'updated_dt')
    search_fields = ('user__id', 'customer_id')
    list_filter = ('created_dt',)


@admin.register(payment_models.CustomerCard)
class CustomerCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_id', 'brand', 'last4', 'created_dt')
    search_fields = ('id', 'card_id', 'user__id')
    list_filter = ('created_dt', 'brand')


@admin.register(payment_models.StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'count', 'created_dt', 'updated_dt')
    search_fields = ('event_id',)
    list_filter = ('created_dt', 'updated_dt')





