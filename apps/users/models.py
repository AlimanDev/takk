import datetime
from typing import Optional
from django.db.models import QuerySet
from fcm_django.models import FCMDevice
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.companies.models import Company
from apps.orders.models import Order

import pytz


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    """Пользователи"""
    COMPANY_OWNER = 1
    EMPLOYEE = 2
    USER = 3
    USER_TYPE_CHOICES = (  # Тип пользователя
        (COMPANY_OWNER, _('Company owner')),
        (EMPLOYEE, _('Employee')),
        (USER, _('User')),
    )
    ANDROID = 'android'
    IOS = 'ios'
    NOT_OS = 'unknown'
    username = models.CharField(
        _('Name'), max_length=50, null=True)
    phone = models.CharField(
        _('Phone number'), max_length=20, unique=True)
    sms_code = models.IntegerField(  # код отправленный по номеру phone
        _('SMS code'), blank=True, null=True)
    user_type = models.PositiveSmallIntegerField(
        _('User type'), choices=USER_TYPE_CHOICES, default=USER)
    phone_is_verified = models.BooleanField(
        _('Phone verified'), default=False)
    date_of_birthday = models.DateField(
        _('Date of birthday'), null=True, blank=True)
    avatar = models.ImageField(
        _('Avatar'), upload_to='users/avatar', null=True)
    referral_code = models.CharField(
        _('Referral code'), max_length=60, null=True)
    balance = models.DecimalField(
        _('Balance'), decimal_places=2, default=0.0, max_digits=10)
    is_auto_fill = models.BooleanField(  # TODO: риализовать auto-fill
        _('Auto fill'), default=False)
    auto_fill_tariff = models.ForeignKey(
        'BudgetTariff', on_delete=models.SET_NULL, null=True)
    favorite_cafes = models.ManyToManyField(
        'companies.Cafe', blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'phone'
    # REQUIRED_FIELDS = ['phone']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'

    def __str__(self):
        return '%s %s ' % (self.phone, self.user_type)

    def get_balance_in_cents(self) -> int:
        return int(float(self.balance) * 100)

    def get_balance_float(self) -> float:
        return round(float(self.balance), 2)

    def get_free_items(self, company_id) -> QuerySet:
        return self.free_items.filter(status='valid', company_id=company_id)

    def get_company_points(self, company: Company) -> 'Point':
        points, _ = Point.objects.get_or_create(company=company, user=self)
        return points

    def get_cards(self) -> QuerySet:
        return self.cards.all()

    def get_orders(self) -> QuerySet:
        return self.orders.exclude(status=Order.WAITING)

    def get_last_order(self) -> Optional[Order]:
        orders = self.get_orders()
        if orders.exists():
            return orders.first()
        return None

    def get_last_order_date(self) -> Optional[int]:
        last_order = self.get_last_order()
        if last_order:
            return int(last_order.created.timestamp() * 1000)
        return None

    def get_os_type(self) -> str:
        mobile = FCMDevice.objects.filter(user=self, active=True)
        if mobile.exists():
            return mobile.first().type
        return 'unknown'

    def get_customer_name(self) -> str:
        username = self.username if self.username else f'user ID: {self.id}'
        return f'{self.username} phone: {self.phone}'


class BudgetTariff(models.Model):
    """Тарифы бюджета"""
    amount_payout = models.DecimalField(  # Сумма выплаты
        _('Amount of payout'), decimal_places=2, max_digits=10)
    amount_receipt = models.DecimalField(  # Сумма получения
        _('Amount of receipt'), decimal_places=2, max_digits=10)
    percent = models.PositiveSmallIntegerField(  # Скидка на выплату за тариф
        _('Perсent'), default=0)

    class Meta:
        verbose_name = _('Tariff')
        verbose_name_plural = _('Tariffs')
        db_table = 'budget_tariffs'

    def get_amount_payout_in_cents(self) -> int:
        return int(float(self.amount_payout) * 100)

    def get_amount_receipt_in_cents(self) -> int:
        return int(float(self.amount_receipt) * 100)


class BudgetFillHistory(models.Model):
    """История автопополнений бюджета пользователя"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='fill_histories')
    transaction = models.ForeignKey(
        'payment.BudgetTransaction', on_delete=models.SET_NULL, null=True)
    tariff = models.ForeignKey(
        BudgetTariff, verbose_name=_('Tariff'), on_delete=models.SET_NULL, null=True)
    amount_payout = models.DecimalField(  # Сумма выплаты
        _('Amount of payout'), decimal_places=2, max_digits=10)
    amount_receipt = models.DecimalField(  # Сумма получения
        _('Amount of receipt'), decimal_places=2, max_digits=10)
    created_dt = models.DateTimeField(
        _('Last fill date'), auto_now_add=True)

    class Meta:
        verbose_name = _('Fill History')
        verbose_name_plural = _('Fill Histories')
        db_table = 'budget_fill_history'

    def __str__(self) -> str:
        return f'User - {self.user.phone}'

    def get_created_dt_timestamp(self) -> int:
        return int(self.created_dt.timestamp() * 1000)


class CashbackHistory(models.Model):
    """Когда и сколько было получено кешбека"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cashback_histories')
    date = models.DateTimeField(
        _('Date'), auto_now_add=True)
    amount = models.DecimalField(
        _('Amount'), max_digits=10, decimal_places=2)
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('Cashback History')
        verbose_name_plural = _('Cashback Histories')
        db_table = 'user_cashback_history'


class InvitedUser(models.Model):
    """Приглашенные пользователи"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='invited')
    inviter = models.ForeignKey(
        User, on_delete=models.CASCADE)
    given_free_item = models.BooleanField(
        default=True)

    class Meta:
        verbose_name = _('Invited User')
        verbose_name_plural = _('Invited Users')
        db_table = 'invited_users'


class FreeItem(models.Model):
    """
    Бесплатный продукт пользователя
    Когда Point пользователя достигает Company.exchangeable_point, создаётся Freeitem а Point обнуляется
    FreeItem имеет срок действия  Company.expiration_days
    """

    VALID = 'valid'
    EXPIRED = 'expired'
    REDEEMED = 'redeemed'
    STATUS_CHOICES = (
        (VALID, 'Valid'),
        (EXPIRED, 'Expired'),
        (REDEEMED, 'Redeemed'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='free_items', on_delete=models.CASCADE)
    company = models.ForeignKey(  # К какой компании относется
        Company, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(  # На какой продукт был обменен
        'products.Product', null=True, blank=True, on_delete=models.SET_NULL)
    created_dt = models.DateTimeField(  # Дата получения
        auto_now_add=True)
    expiration_dt = models.DateTimeField(  # Срок дейтвия
        null=True, blank=True)
    status = models.CharField(  # Статус
        choices=STATUS_CHOICES, default=VALID, max_length=60)

    class Meta:
        db_table = 'free_item'
        ordering = ('-created_dt', )

    def __str__(self) -> str:
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expiration_dt = datetime.datetime.now(pytz.UTC) + datetime.timedelta(
                days=self.company.expiration_days)
        super().save(*args, **kwargs)

    def check_expiration_day(self) -> bool:
        date_now = datetime.datetime.now(pytz.UTC)
        if date_now < self.expiration_dt:
            return True
        else:
            self.status = self.EXPIRED
            self.save(update_fields=['status', ])
            return False

    def get_expiration_dt_timestamp(self) -> int:
        return int(self.expiration_dt.timestamp() * 1000)

    def get_created_dt_timestamp(self) -> int:
        return int(self.created_dt.timestamp() * 1000)


class Point(models.Model):
    """Бонусные баллы"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='points', on_delete=models.CASCADE)
    company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        auto_now_add=True)
    points = models.PositiveIntegerField(
        default=0)

    class Meta:
        db_table = 'points'

    def __str__(self) -> str:
        return 'Company: {} User id: {} points: {}'.format(self.company.name, self.user.pk, self.points)


class UserNotification(models.Model):
    """ Уведомления пользователя """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(
        max_length=255)
    body = models.CharField(
        max_length=255)
    created_dt = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        db_table = 'user_notifications'
        ordering = ('-created_dt',)

    def __str__(self) -> str:
        return 'User_id:{} {}'.format(self.user.pk, self.title)

    def get_created_dt_timestamp(self) -> int:
        return int(self.created_dt.timestamp() * 1000)

# class UserMessage(models.Model):
#     """ Сообщение """
#     sender = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='messages')
#     order = models.ForeignKey(
#         'orders.Order', on_delete=models.SET_NULL, null=True)
#     company = models.ForeignKey(
#         'companies.Company', on_delete=models.SET_NULL, null=True)
#     title = models.CharField(
#         null=True, blank=True)
#     message = models.TextField()
#     answer_to_message = models.TextField(
#         null=True, blank=True)
#     created_dt = models.DateTimeField(
#         auto_now_add=True)
#
#     class Meta:
#         db_table = 'user_messages'
#
#     def save(self, *args, **kwargs):
#         if self.company:
#             self.title = '{} {}'
#         super(UserMessage, self).save(*args, **kwargs)