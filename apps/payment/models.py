from django.db import models
from apps.orders import models as order_models
from django.conf import settings


class OrderPaymentTransaction(models.Model):
    """Транзакция заказа"""
    ONLINE = 0  # онлайн оплата замараживаем деньги 1 день. Для оплат с карты или Google, Apple pay без сохранения карты
    BALANCE = 1  # оплата с баланса клиента
    CARD = 2  # Когда пользователь только сохраняет карту замараживаем деньги на 1 день
    CARD_CHARGE = 3  # Уже доверенный пользователь можем замараживать все транзакции с нимать их в одной транзакции
    TERMINAL = 3  # Оплата с терминала
    PAID = 0  # Оплачено
    REFUND = 1  # Деньги были частично или полность вернули клиенту

    PAYMENT_TYPE = (
        (ONLINE, 'Online payment'),
        (BALANCE, 'Balance payment'),
        (CARD, 'Save card payment'),
        (TERMINAL, 'Terminal payment'),

    )
    STATUS = (
        (PAID, 'Paid'),
        (REFUND, 'Refund')
    )

    customer = models.ForeignKey(  # Клиент
        'users.User', on_delete=models.SET_NULL, null=True, related_name='order_transactions')
    employee = models.ForeignKey(  # Сотрудник который сделал refund
        'users.User', on_delete=models.SET_NULL, null=True, related_name='refund_transactions')
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, null=True)
    order_detail = models.TextField(
        null=True, max_length=2500)
    cafe = models.ForeignKey(
        'companies.Cafe', on_delete=models.SET_NULL, null=True)
    card = models.ForeignKey(  # сохраненная карта клиента
        'CustomerCard', on_delete=models.SET_NULL, null=True)
    last4 = models.CharField(  # последние 4 цифры карты
        max_length=4, null=True)
    brand = models.CharField(  # тип карты
        max_length=100, null=True)
    final_transaction = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, related_name='children')
    payment_id = models.CharField(  # PaymentIntent id из Stripe
        max_length=250, null=True)
    amount = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2, default=0)  # Сумма транзакции
    takk_fee = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2, default=0)
    stripe_fee = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2, default=0)
    customer_cashback = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2, default=0)
    payment_type = models.SmallIntegerField(
        choices=PAYMENT_TYPE)
    status = models.SmallIntegerField(
        choices=STATUS, default=PAID)
    is_capture = models.BooleanField(  # захват средств после заморозки
        default=True)
    refund_id = models.CharField(  # Refund id из Stripe
        max_length=250, null=True)
    refund_detail = models.TextField(
        null=True, max_length=2500)
    refund_description = models.CharField(  # Описание почему делают refund
        max_length=250, null=True)
    refund_amount = models.IntegerField(
        default=0)
    refund_fee = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2, default=0)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        db_table = 'order_payment_transactions'
        ordering = ('-created_dt', )

    def get_amount_in_float(self):
        return float(self.amount) / 100

    def get_created_dt_timestamp(self):
        return int(self.created_dt.timestamp())

    def get_updated_dt_timestamp(self):
        return int(self.updated_dt.timestamp())


class BudgetTransaction(models.Model):
    """Транзакции которые перечесляются на счет Takk в Stripe
        (для того чтобы пополнить баланс в Такк (mobile)
    """
    payment_id = models.CharField(  # Stripe PaymentIntent id
        max_length=250)
    user = models.ForeignKey(  #
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    tariff = models.ForeignKey(  # какой тариф
        'users.BudgetTariff', on_delete=models.SET_NULL, null=True)
    amount_payout = models.IntegerField()  # in cents  Сумма оплаты
    amount_receipt = models.IntegerField()  # in cents Сумма которую получет клиент
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        db_table = 'budget_transactions'
        ordering = ('-created_dt', )

    def get_created_dt_timestamp(self):
        return int(self.created_dt.timestamp())

    def get_updated_dt_timestamp(self):
        return int(self.updated_dt.timestamp())


class StripeCustomer(models.Model):
    """ Клиенты Stripe """

    user = models.OneToOneField(
        'users.User', on_delete=models.CASCADE, null=True, related_name='stripe_customer')
    customer_id = models.CharField(  # Customer ID in Stripe
        max_length=250, blank=True, null=True)
    is_verified = models.BooleanField(
        default=False)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        db_table = 'stripe_customer'


class CustomerCard(models.Model):
    """Карты пользователя """

    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, null=True, related_name='cards')
    card_id = models.CharField(
        max_length=250, null=True)
    brand = models.CharField(
        max_length=10)
    last4 = models.CharField(
        max_length=4)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    name = models.CharField(
        max_length=250, null=True)
    is_confirm_off_session = models.BooleanField(
        default=True)
    is_default = models.BooleanField(
        default=False)

    class Meta:
        db_table = 'customer_cards'

    def __str__(self) -> str:
        return f'User - {self.user_id} cart_id - {self.card_id}'

    def get_created_dt_timestamp(self) -> int:
        return int(self.created_dt.timestamp() * 1000)


class StripeWebhookEvent(models.Model):
    """ События """
    event_id = models.CharField(
        max_length=250)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    count = models.IntegerField(  # Для теста чтобы знать сколько раз пришло событие
        default=1)
    updated_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        db_table = 'stripe_webhook_event'


# class OrderRefundTransaction(models.Model):
#     """ Возврат денег клиентам """
#     FULL_REFUND = 0
#     PARTIAL_REFUND = 1
#     REFUND_TYPE = (
#         (FULL_REFUND, 'Full refund order amount'),
#         (PARTIAL_REFUND, 'Partial refund order amount'),
#     )
#     transaction = models.ForeignKey(
#         OrderPaymentTransaction, on_delete=models.CASCADE)
#     refund_type = models.SmallIntegerField(
#         default=FULL_REFUND, choices=REFUND_TYPE)
#     employee = models.ForeignKey(
#         'users.User', on_delete=models.SET_NULL, null=True, related_name='refund_orders')
#     is_refund = models.BooleanField(
#         default=False)
#     refund_amount = models.DecimalField(
#         )
#     refund_detail = models.TextField(
#         null=True)
#     created_dt = models.DateTimeField(
#         auto_now_add=True)
#     updated_dt = models.DateTimeField(
#         auto_now=True)
#
#     class Meta:
#         db_table = 'order_refund_transaction'
#         ordering = ('-created_dt',)
