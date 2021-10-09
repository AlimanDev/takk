import datetime
import pytz

from timezone_field import TimeZoneField
from localflavor.us.models import USStateField
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import Point
from django.contrib.gis.db import models


class Company(models.Model):
    """ Компания """
    owner = models.ForeignKey(  # Владелец компании
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Company owner'))
    is_activate = models.BooleanField(  # Будет ли компании выводится в приложении (может изменять только владелец ТАКК)
        default=False, verbose_name=_('Company status'))
    name = models.CharField(
        _('Company name'), max_length=100)
    phone = models.CharField(  # Рабочий телефон компании
        max_length=15, null=True, blank=True)
    email = models.EmailField(
        null=True, blank=True, unique=True)
    ex_point = models.PositiveSmallIntegerField(  # FIXME УДАЛИТЬ
        _('Exchange point'), default=10)
    validity_point_day = models.PositiveSmallIntegerField(  # FIXME УДАЛИТЬ
        _('Exchange validity point'), default=30)
    pub_show_reviews = models.BooleanField(  # Будут ли отзывы отоброжатся для всех публично
        _('Make reviews public'), default=True)
    pub_show_like = models.BooleanField(  # Будут ли лайки отоброжатся для всех публично
        _('Make like public'), default=True)
    cashback_percent = models.FloatField(
        default=5)
    logo = models.ImageField(
        _('Company Logo'), upload_to='companies/logos')
    logo_resized = ImageSpecField(
        source='logo', processors=[ResizeToFill(256, 256)], format='JPEG', options={'quality': 100})
    loading_app_image = models.ImageField(  # Изображение загрузочного экрана в приложении
        _('App image'), upload_to='companies/app')
    app_image_morning = models.ImageField(  # Утреннее фоновое изоб в приложении
        _('Background image in the morning'), upload_to='companies/app')
    app_image_day = models.ImageField(  # Дневное фоновое изоб в приложении
        _('Background image in the afternoon'), upload_to='companies/app')
    app_image_evening = models.ImageField(  # Вечерние фоновое изоб в приложении
        _('Background image in evening'), upload_to='companies/app')
    exchangeable_point = models.IntegerField(  # Сколько Points нужно нобрать чтобы получить FreeItem
        default=10)
    expiration_days = models.IntegerField(  # Срок действия FreeItem
        default=30)
    about = models.CharField(
        max_length=1500, null=True, blank=True)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        db_table = 'companies'

    def __str__(self):
        return self.name

    def get_created_dt_timestamp(self):
        return int(self.created_dt.timestamp() * 1000)

    def get_updated_dt_timestamp(self):
        return int(self.updated_dt.timestamp() * 1000)


class Menu(models.Model):  # Если его переместить в products.models то происходит ошибка(зацикленный импорт)
    """Меню кафе"""
    company = models.ForeignKey(  # К какой компании относется меню
        Company, on_delete=models.CASCADE, related_name='company_menus')
    name = models.CharField(
        max_length=50)

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
        db_table = 'menus'

    def __str__(self):
        return 'id:{} {}'.format(self.id, self.name)

    def get_product_category_count(self) -> int:
        return self.categories.count()

    def get_product_count(self) -> int:  # TODO использовать annotate
        count = 0
        categories = self.categories.all()
        if categories:
            for c in categories:
                count += c.products.count()
        return count


class Cafe(models.Model):
    """ Кафе """
    BLOCKED = 0
    ACTIVE = 1
    PENDING = 2
    STATUS = (  # Может менять только владелец компании или ТАКК пользователь
        (BLOCKED, _('Blocked')),
        (ACTIVE, _('Active')),
        (PENDING, _('Pending')),
    )

    company = models.ForeignKey(  # К какой канпании относится кафе
        Company, on_delete=models.CASCADE, related_name='cafes', null=True)
    menu = models.ForeignKey(
        Menu, on_delete=models.SET_NULL, null=True, related_name='cafes', blank=True)
    logo = models.ImageField(
        _('Cafe logo'), upload_to='cafe/logo')
    logo_small = ImageSpecField(
        source='logo', processors=[ResizeToFill(190, 280)], format='JPEG', options={'quality': 100})
    logo_medium = ImageSpecField(
        source='logo', processors=[ResizeToFill(300, 500)], format='JPEG', options={'quality': 90})
    logo_large = ImageSpecField(
        source='logo', processors=[ResizeToFill(500, 700)], format='JPEG', options={'quality': 80})
    name = models.CharField(
        _('Cafe name'), max_length=255)
    description = models.TextField(  # Описание компании
        _('Description cafe'), null=True)
    call_center = models.CharField(
        max_length=50, verbose_name='Phone')
    website = models.CharField(
        null=True, blank=True, max_length=250)
    status = models.IntegerField(
        choices=STATUS, default=BLOCKED)

    location = models.PointField(
        geography=True, default=Point(0.0, 0.0))

    country = models.CharField(
        null=True, max_length=50)
    city = models.CharField(
        null=True, blank=True, max_length=220)
    state = models.CharField(
        null=True, max_length=250)
    postal_code = models.CharField(
        null=True, max_length=12)
    address = models.TextField(
        null=True, blank=True, verbose_name=_('Address 1'))
    second_address = models.TextField(
        null=True, blank=True, verbose_name=_('Address 2'))
    tax_rate = models.DecimalField(  # Налоговый показатель
        max_digits=100, decimal_places=3)
    cafe_timezone = TimeZoneField(
        default=settings.TIME_ZONE)
    delivery_available = models.BooleanField(  # Есть ли доставка товаров
        null=False, default=False)
    delivery_max_distance = models.IntegerField(  # Максимальная дистанция доставки
        null=True, default=0)
    delivery_min_amount = models.DecimalField(  # Минимальная плата доставки
        max_digits=10, decimal_places=2, default=0.0)
    delivery_fee = models.DecimalField(  # Плата доставки
        max_digits=10, decimal_places=2, default=0.0)
    delivery_percent = models.DecimalField(  # Процент доставки
        max_digits=10, decimal_places=2, default=0.0)
    delivery_km_amount = models.DecimalField(  # Цена за каждый километр (Доставки)
        max_digits=10, decimal_places=2, default=0.0)
    delivery_min_time = models.IntegerField(  # Время доставки
        default=30)
    version = models.PositiveIntegerField(  # Версия нужно для приложения
        blank=True, default=1)
    order_limit = models.IntegerField(  # макс. 10 заказов за время order_limit_time
        default=10, verbose_name='Order limit per window', blank=True)
    order_time_limit = models.IntegerField(  # каждые 10 мин. максимальное order_limit
        default=10, verbose_name='Order limit window', blank=True)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name = 'Cafe'
        verbose_name_plural = 'Cafes'
        db_table = 'cafes'

    def __str__(self):
        return 'ID {} {}'.format(self.id, self.name)

    @property
    def longitude(self):
        return self.location.x

    @property
    def latitude(self):
        return self.location.y

    def get_is_open_now(self):
        """Открыто ли кафе сайчас"""
        days = {
            0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'friday',
            5: 'saturday',
            6: 'sunday'
        }

        cafe_tz = pytz.timezone(str(self.cafe_timezone))
        cafe_dt_now = datetime.datetime.now(cafe_tz)
        work_day = self.week_time.get(day=days[cafe_dt_now.weekday()])

        if not work_day.is_open:
            return False
        if work_day.opening_time < cafe_dt_now.time() < work_day.closing_time:
            return True

        return True

    def get_opening_time(self):

        days = {
            0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'friday',
            5: 'saturday',
            6: 'sunday'
        }
        cafe_tz = pytz.timezone(str(self.cafe_timezone))
        cafe_dt_now = datetime.datetime.now(cafe_tz)
        work_day = self.week_time.get(day=days[cafe_dt_now.weekday()])
        return work_day.opening_time

    def get_closing_time(self):

        days = {
            0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'friday',
            5: 'saturday',
            6: 'sunday'
        }
        cafe_tz = pytz.timezone(str(self.cafe_timezone))
        cafe_dt_now = datetime.datetime.now(cafe_tz)
        work_day = self.week_time.get(day=days[cafe_dt_now.weekday()])
        return work_day.closing_time

    def get_created_dt_timestamp(self):
        return int(self.created_dt.timestamp())

    def get_updated_dt_timestamp(self):
        return int(self.updated_dt.timestamp())

    def get_employees(self):
        employees = self.employees.all()
        return employees


class Employee(models.Model):
    """Сотрудники компании"""
    Manager = 1
    Cashier = 2
    EMPLOYEE_POSITION_CHOICES = (  # Должность сотрудника
        (Manager, 'Manager'),
        (Cashier, 'Cashier'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee')
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE)
    cafes = models.ManyToManyField(  # Список кафе этой компании к которым дан доступ сотруднику
        'Cafe', related_name='employees', blank=True)
    created_by = models.ForeignKey(  # Кто создал сотрудника
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='employees')
    created_dt = models.DateTimeField(
        auto_now_add=True)
    employee_position = models.SmallIntegerField(  # Должность сотрудника
        choices=EMPLOYEE_POSITION_CHOICES)

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        db_table = 'employees'

    def get_created_dt_timestamp(self):
        return int(self.created_dt.timestamp())


class CafePhoto(models.Model):
    """Фотографии Кафе"""
    cafe = models.ForeignKey(
        Cafe, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(
        upload_to='cafe/album')
    image_small = ImageSpecField(
        source='image', processors=[ResizeToFill(190, 280)], format='JPEG', options={'quality': 100})

    class Meta:
        verbose_name = 'Cafe Photo'
        verbose_name_plural = 'Cafe Photos'
        db_table = 'cafe_photos'


class CafeWeekTime(models.Model):
    """График работы кафе """
    WEEK_DAYS = (
        ('monday', _('Monday'),),
        ('tuesday', _('Tuesday'),),
        ('wednesday', _('Wednesday'),),
        ('thursday', _('Thursday'),),
        ('friday', _('Friday'),),
        ('saturday', _('Saturday'),),
        ('sunday', _('Sunday'),),
    )
    cafe = models.ForeignKey(
        Cafe, null=True, related_name='week_time', on_delete=models.CASCADE)
    day = models.CharField(
        choices=WEEK_DAYS, max_length=15)
    is_open = models.BooleanField(  # Если True то нужно указать opening_time и closing_time
        default=True)
    opening_time = models.TimeField(
        null=True, blank=True)
    closing_time = models.TimeField(
        null=True, blank=True)

    class Meta:
        verbose_name = 'Cafe Week Time'
        verbose_name_plural = 'Cafes Week Time'
        db_table = 'cafes_week_time'


class CompanyCard(models.Model):
    """ Карты компании """
    account_id = models.CharField(  # ID аккаунта Stripe
        max_length=250)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=250)
    email = models.CharField(
        max_length=250)
    is_default = models.BooleanField(
        default=False)
    created_dt = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        db_table = 'company_card'


class TakkFeeForCompany(models.Model):
    """ Налог TAKK для компаний """
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, unique=True)
    is_percent = models.BooleanField(  # Тип налога fee_percent или fee_amount за каждый
        default=False)
    fee_percent = models.SmallIntegerField(
        null=True, blank=True)
    fee_amount = models.DecimalField(  # in cents
        null=True, blank=True, decimal_places=2, max_digits=10, default=0)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    update_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        db_table = 'takk_fee_for_company'


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class TakkGeneralSettings(SingletonModel):

    cashback = models.FloatField(
        default=5)
    updated_dt = models.DateTimeField(
        auto_now=True)
    charge_limit = models.IntegerField(
        default=2500)

    class Meta:
        db_table = 'takk_general_settings'

    def get_charge_limit(self):
        return self.charge_limit


# class CafeNotificationHistory(models.Model):
#     """Уведомления для экрана """
#     cafe = models.ForeignKey(
#         'Cafe', on_delete=models.CASCADE)
#     order = models.ForeignKey(
#         'orders.Order', on_delete=models.SET_NULL, null=True)
#
