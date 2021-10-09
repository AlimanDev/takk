from apps.users import models as user_models
from rest_framework.exceptions import ValidationError
from apps.restapi import exceptions as my_exception
from apps.companies import models as company_models
from apps.products import models as product_models


def get_user(phone):
    # должен вернуть пользователя или None
    try:
        if phone:
            user = user_models.User.objects.get(phone=phone)
            return user
        return None
    except user_models.User.DoesNotExist:
        return None

########################
# MENU DUPLICATE LOGIC #
########################


def duplicate_menu(menu: company_models.Menu, name: str) -> company_models.Menu:

    new_menu = company_models.Menu.objects.create(
        name=name, company=menu.company)
    new_modifiers = duplicate_modifiers(  # key -> id modifier menu которое дублируется, value -> продублированный mod
        menu, new_menu)
    new_categories_parent = duplicate_category_parent(  # тоже самое как new_modifiers
        menu, new_menu)

    for category in menu.categories.all():
        if category.parent:
            new_category = create_category_duplicate(new_menu, category)
            new_category.parent = new_categories_parent.get(category.id)
            new_category.save()
        else:
            new_category = new_categories_parent.get(category.id)
        duplicate_products(category, new_category, new_modifiers)

    return new_menu


def duplicate_modifiers(menu: company_models.Menu, new_menu: company_models.Menu) -> dict:
    new_modifiers = {}  # это нужно для того чтобы связать новые продукты с новыми modifier
    modifiers = menu.modifiers.all()
    if modifiers.exists():
        for modifier in modifiers:
            new_modifier = create_modifier_duplicate(new_menu, modifier)  # дублирует modifier
            new_modifiers[modifier.id] = new_modifier
            for mod_item in modifier.items.all():
                create_modifier_item_duplicate(new_modifier, mod_item)
    return new_modifiers


def duplicate_products(category: product_models.ProductCategory,
                       new_category: product_models.ProductCategory, new_modifiers: dict):
    products = category.products.all()
    if products.exists():
        for product in products:
            new_product = create_product_duplicate(new_category, product)
            product_sizes = product.sizes.all()
            if product_sizes.exists():  # duplicate sizes
                for product_size in product_sizes:
                    create_product_size_duplicate(new_product, product_size)
            product_modifiers = product.modifiers.all()
            if product_modifiers.exists():  # add modifiers
                for product_modifier in product_modifiers:
                    mod = new_modifiers.get(product_modifier.id)
                    if mod:
                        new_product.modifiers.add(mod)


def duplicate_category_parent(menu: company_models.Menu, new_menu: company_models.Menu) -> dict:
    new_categories = {}  # это нужно для того чтобы связать новые категории с category.parent
    categories = menu.categories.filter(parent__isnull=True)
    if categories.exists():
        for category in categories:

            new_category = create_category_duplicate(new_menu, category)  # дублирует category
            new_categories[category.id] = new_category
    return new_categories


def create_category_duplicate(menu: company_models.Menu,
                              category: product_models.ProductCategory) -> product_models.ProductCategory:
    category_duplicate = product_models.ProductCategory.objects.create(
        menu=menu,
        name=category.name,
        image=category.image,
        available=category.available,
        start=category.start,
        end=category.end,
        position=category.position,
        is_kitchen=category.is_kitchen,
        is_give_point=category.is_give_point,
        is_exchange_free_item=category.is_exchange_free_item
    )
    return category_duplicate


def create_product_duplicate(category: product_models.ProductCategory,
                             product: product_models.Product) -> product_models.Product:
    product_duplicate = product_models.Product.objects.create(
        category=category,
        name=product.name,
        image=product.image,
        description=product.description,
        position=product.position,
        start=product.start,
        end=product.end,
        quickest_time=product.quickest_time,
        tax_percent=product.tax_percent)
    return product_duplicate


def create_product_size_duplicate(product: product_models.Product, product_size: product_models.ProductSize):

    product_models.ProductSize.objects.create(
        product=product,
        name=product_size.name,
        price=product_size.price,
        available=product_size.available,
        default=product_size.default
    )


def create_modifier_duplicate(menu: company_models.Menu,
                              modifier: product_models.Modifier) -> product_models.Modifier:
    modifier_duplicate = product_models.Modifier.objects.create(
        menu=menu,
        name=modifier.name,
        is_single=modifier.is_single,
        required=modifier.required,
        available=modifier.available,
        position=modifier.position
    )
    return modifier_duplicate


def create_modifier_item_duplicate(modifier: product_models.Modifier,
                                   modifier_item: product_models.ModifierItem):
    product_models.ModifierItem.objects.create(
        modifier=modifier,
        name=modifier_item.name,
        price=modifier_item.price,
        available=modifier_item.available,
        default=modifier_item.default,
        position=modifier_item.position
    )

############################
# MENU DUPLICATE LOGIC END #
############################
