import datetime

from django.db import models
from imagekit.processors import ResizeToFit, Adjust, ResizeToFill
from ckeditor.fields import RichTextField
from apps.companies import models as company_models
from mptt.models import MPTTModel, TreeForeignKey
from imagekit.models import ProcessedImageField, ImageSpecField

from apps.companies.models import Menu


class Modifier(models.Model):
    """Модификаторы продукта"""
    menu = models.ForeignKey(
        company_models.Menu, on_delete=models.CASCADE, related_name='modifiers')
    name = models.CharField(
        max_length=250)
    is_single = models.BooleanField(  # Допускает выбор только одного ModifierItem
        default=True)
    required = models.BooleanField(  # Обязательный выбор ModifierItem
        default=True)
    available = models.BooleanField(  # Отоброжать ли в списке Modifier
        default=True)
    position = models.PositiveIntegerField(
        default=1)  # Нужен для сортировки в дашборде
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name = 'Modifier'
        verbose_name_plural = 'Modifiers'
        db_table = 'modifiers'
        ordering = ('-id',)

    def get_created_dt_timestamp(self):
        return int(self.created_dt.timestamp())

    def get_updated_dt_timestamp(self):
        return int(self.updated_dt.timestamp())


class ModifierItem(models.Model):
    """Модификатор"""
    modifier = models.ForeignKey(
        Modifier, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(
        max_length=250)
    price = models.DecimalField(
        decimal_places=2, max_digits=10, default=0)
    available = models.BooleanField(  # Отоброжать ли в списке ModifierItem
        default=True)
    default = models.BooleanField(  # Будет выбрано по умолчанию при покупке товара
        default=True)
    position = models.PositiveIntegerField(
        default=1)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name = 'Modifier Item'
        verbose_name_plural = 'Modifier Items'
        db_table = 'modifier_items'
        ordering = ('-id',)

    def get_created_dt_timestamp(self):
        return int(self.created_dt.timestamp())

    def get_updated_dt_timestamp(self):
        return int(self.updated_dt.timestamp())


class ProductCategory(MPTTModel):
    """Категория продуктов"""
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name='categories')
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    name = models.CharField(
        max_length=100)
    image = models.ImageField(
        upload_to='products/category/%y/%m/%d')
    image_small = ImageSpecField(
        processors=[ResizeToFill(50, 50)], source='image', options={'quality': 90}, format='JPEG')
    image_medium = ImageSpecField(
        processors=[ResizeToFill(240, 240)], source='image', options={'quality': 90}, format='JPEG')
    image_large = ImageSpecField(
        processors=[ResizeToFill(640, 480)], source='image', options={'quality': 90}, format='JPEG')
    available = models.BooleanField(  # Доступна ли эта категория
        default=True)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)
    start = models.TimeField(  # С какого времени доступно эта катигория
        null=True)
    end = models.TimeField(  # До какого времени дос-кат
        null=True)
    position = models.PositiveIntegerField(
        default=1)
    is_kitchen = models.BooleanField(
        default=False)
    is_give_point = models.BooleanField(  # при покупке продукта с этой категории получает point
        default=False)
    is_exchange_free_item = models.BooleanField(  # можно ли обменять продукт с этой категории на free item
        default=False)

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'
        db_table = 'product_categories'
        ordering = ('-id',)

    def get_start_time(self):
        if self.start:
            return self.start
        elif self.parent and self.parent.start:
            return self.parent.start
        else:
            return datetime.datetime.now().time()  # FIXME: нужно убрать это логику (для теста)

    def get_end_time(self):
        if self.end:
            return self.end
        elif self.parent and self.parent.end:
            return self.parent.end
        else:
            return datetime.datetime.now().time()  # FIXME: нужно убрать это логику (для теста)

    def get_created_dt_timestamp(self):
        return int(self.created_dt.timestamp())

    def get_updated_dt_timestamp(self):
        return int(self.updated_dt.timestamp())


class Product(models.Model):
    """Продукты"""
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name='products')
    modifiers = models.ManyToManyField(
        Modifier, blank=True)
    image = ProcessedImageField(
        upload_to='products/%y/%m/%d')
    image_small = ImageSpecField(
        processors=[ResizeToFill(50, 50)], source='image', options={'quality': 90}, format='JPEG')
    image_medium = ImageSpecField(
        processors=[ResizeToFill(240, 240)], source='image', options={'quality': 90}, format='JPEG')
    image_large = ImageSpecField(
        processors=[ResizeToFill(640, 480)], source='image', options={'quality': 90}, format='JPEG')
    name = models.CharField(
        max_length=150)
    description = models.TextField(
        blank=True, null=True)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)
    position = models.PositiveIntegerField(
        default=1)
    start = models.TimeField(  # С какого времени доступно этот продукт
        null=True, blank=True)
    end = models.TimeField(  # До какого времени дос-пр
        null=True, blank=True)
    quickest_time = models.TimeField(  # Время готовки
        null=True, blank=True)
    tax_percent = models.PositiveSmallIntegerField(  # Процент tax_rate из модели Cafe
        default=0)
    # available = models.BooleanField(
    #     default=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'products'
        ordering = ('-id',)

    def get_sub_category_id(self) -> int:
        return self.category.id

    def get_category_id(self) -> int:
        return self.category.parent.id

    def product_is_free(self) -> bool:
        return True if self.category.is_exchange_free_item else False

    def get_size_ids(self) -> list:
        return self.sizes.all().values_list('id', flat=True)

    def get_start_time(self) -> datetime.time:
        if self.start:
            return self.start
        else:
            return self.category.get_start_time()

    def get_end_time(self) -> datetime.time:
        if self.end:
            return self.end
        else:
            return self.category.get_end_time()

    def get_created_dt_timestamp(self):
        return int(self.created_dt.timestamp())

    def get_updated_dt_timestamp(self):
        return int(self.updated_dt.timestamp())


class ProductSize(models.Model):
    """Размеры продукта"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='sizes')
    name = models.CharField(
        max_length=250)
    price = models.DecimalField(
        max_digits=10, decimal_places=2)
    available = models.BooleanField(  # Доступен или нет
        default=True)
    default = models.BooleanField(  # Дефаултный размер продукта
        default=False)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    updated_dt = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name = 'Product Size'
        verbose_name_plural = 'Product Sizes'
        db_table = 'product_sizes'
        ordering = ('-id',)


class CafeProductState(models.Model):
    """ Продукты кафе (есть в наличии или нет)"""
    cafe = models.ForeignKey(
        'companies.Cafe', on_delete=models.CASCADE, related_name='not_available_products')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cafe_products_state'
