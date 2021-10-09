import json
from django.core.files import File
from urllib.request import urlopen
from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
import datetime
from django.core.management.base import BaseCommand
from apps.users import models as user_models
from apps.companies import models as company_models
from apps.products import models as product_models
from apps.orders import models as order_models
from django.forms import model_to_dict
from django.contrib.gis.geos import Point
from sheet2dict import Worksheet
from django.core.files.temp import NamedTemporaryFile
import imghdr


def get_data(path: str) -> list:
    ws = Worksheet()
    data = ws.xlsx_to_dict(path=f"{path}.xlsx").sheet_items

    return data


def get_gio_cafe(cafe_id: str) -> Point:
    if cafe_id == '10':
        return Point(x=float(40.71536), y=float(-74.01100))
    if cafe_id == '13':
        return Point(x=float(40.75506), y=float(-73.98009))
    if cafe_id == '17':
        return Point(x=float(39.75420), y=float(-105.00089))
    if cafe_id == '18':
        return Point(x=float(39.74710), y=float(-104.99881))
    if cafe_id == '22':
        return Point(x=float(40.72110), y=float(-74.00983))
    else:
        return Point(x=0, y=0)


def get_cafe_product_list(cafe_id: int) -> list:
    data = dict()
    file_path = f'export/cafe{cafe_id}.json'
    with open(file_path) as file:
        data = json.load(file)
    return data.get('list')


def get_category_data(category_id):
    data = get_data("export/product category")
    for d in data:
        if str(category_id) == d.get('id'):
            return d
    return None


def save_image(url):
    if url:
        image = NamedTemporaryFile()
        image.write(urlopen(url).read())
        image.flush()
        return image
    return None


def create_category(category: dict, menu):

    obj = product_models.ProductCategory()
    obj.menu = menu
    obj.name = category.get('name')
    if category.get('icon'):
        name = f"m{menu.id}c{category.get('id')}"
        obj.image.save(name, File(save_image(category.get('icon'))))
    if category.get('start') and not category.get('start') == 'None':
        obj.start = datetime.datetime.strptime(category.get('start'), '%H:%M:%S')
    if category.get('end') and not category.get('end') == 'None':
        obj.end = datetime.datetime.strptime(category.get('end'), '%H:%M:%S')

    obj.save()
    return {'category': category.get('id'), 'obj': obj}


def create_products(products, category):
    if products:
        product_list = list()
        for prod in products:
            p = product_models.Product()
            p.category = category
            p.name = prod.get('title')
            p.description = prod.get('description')
            if not prod.get('start') == 'None':
                p.start = datetime.datetime.strptime(prod.get('start'), '%H:%M:%S')
            if not prod.get('end') == 'None':
                p.end = datetime.datetime.strptime(prod.get('end'), '%H:%M:%S')
            if not prod.get('quickest_time') == 'None':
                p.quickest_time = datetime.datetime.strptime(prod.get('quickest_time'), '%H:%M:%S')
            p.tax_percent = prod.get('tax_percent')
            image = save_image(prod.get('images')[0].get('src'))
            name = f'c{category.id}p{prod["id"]}'
            p.image.save(name, File(image))
            p.save()
            product_list.append({
                'id': prod.get('id'),
                'obj': p
            })
            if prod.get('sizes'):
                for size in prod.get('sizes'):
                    s = product_models.ProductSize()
                    s.product = p
                    s.name = size.get('title')
                    s.price = size.get('price')
                    s.available = size.get('available')
                    s.default = size.get('default')
                    s.save()

            if prod.get('modifiers'):
                for mod in prod.get('modifiers'):
                    m = product_models.Modifier()
                    m.menu = category.menu
                    m.name = mod.get('title')

                    m.is_single = bool(mod.get('is_single'))
                    m.required = bool(mod.get('required'))
                    m.available = bool(mod.get('available'))

                    m.save()
                    p.modifiers.add(m)
                    if mod.get('modifier_items'):
                        for m_i in mod.get('modifier_items'):
                            ob = product_models.ModifierItem()
                            ob.modifier = m
                            ob.name = m_i.get('title')
                            ob.price = m_i.get('price')
                            ob.available = m_i.get('available')
                            ob.default = m_i.get('default')
                            ob.save()
        return product_list
    return None

# def get_cafe_product_ids(cafe_id):
#     product_ids = list()
#     cafe_meals = get_data('export/cafe meals')
#     for cafe_product in cafe_meals:
#         if cafe_product.get('cafe') == cafe_id:
#             product_ids.append(cafe_product.get('product'))
#     return product_ids


# def get_products(cafe_id: str, category_id: str) -> list:
#     cafe_product_ids = get_cafe_product_ids(cafe_id)
#     products = get_data('export/product')
#     product_list = list()
#     for product in products:
#         a = product.get('category')
#         b = product.get('sub_category')
#         c = product.get('id') in cafe_product_ids
#         if c and ((a == category_id and b == 'None') or (b == category_id)):
#             product_list.append(product)
#     return product_list


# def get_category_parent(categories, name):
#     for c in categories:
#         if c.get('name') == name:
#             return c
#         return None


# def get_product_categories(owner_id):
#     data = get_data('export/product category')
#     categories = list()
#     for d in data:
#         if d.get('owner') == owner_id:
#             categories.append(d)
#     return categories


# def create_product(product, category):
#     obj = product_models.Product()
#     obj.category = category
#     obj.name = product.get('title')
#     obj.image = product.get('image')
#     obj.description = product.get('description')
#     obj.position = int(product.get('order'))
#     if not product.get('quickest_time') == 'None':
#         obj.quickest_time = datetime.datetime.strptime(product.get('quickest_time'), '%H:%M:%S')
#     obj.tax_percent = int(product.get('tax_percent'))
#     obj.save()
#     return obj


# def get_size(size_id):
#     sizes = get_data('export/size')
#     for size in sizes:
#         if size.get('id') == size_id:
#             return size
#     return None


# def get_sizes(product_id):
#     profiles = get_data('export/product profile')
#     sizes = list()
#     for profile in profiles:
#         if profile.get('product') == product_id:
#
#             size = get_size(profile.get('variations'))


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.delete_users()
        users = self.create_users()
        company = self.create_company(users)
        cafes = self.create_cafes(company)
        cafes = self.create_menu(cafes, company)
        cafes = self.create_cafe_products(cafes)

    @staticmethod
    def delete_users():
        users = user_models.User.objects.exclude(phone='7777').delete()
        company_models.Company.objects.all().delete()

    @staticmethod
    def create_users():
        users = get_data('export/user')
        for user in users:
            obj = user_models.User()
            if not user.get('first_name') == 'None':
                obj.first_name = user.get('first_name')
            if not user.get('last_name') == 'None':
                obj.last_name = user.get('last_name')
            if not user.get('password') == 'None':
                obj.password = user.get('password')
            if not user.get('email') == 'None':
                obj.email = user.get('email')
            if not user.get('password') == 'None':
                obj.password = user.get('password')
            # if not user.get('date_joined') == 'None':
            #     obj.date_joined = datetime.datetime.strptime(user.get('date_joined'), '%Y-%m-%d %H:%M:%S')
            # if not user.get('date_of_birthday') == 'None':
            #     obj.date_of_birthday = datetime.datetime.strptime(user.get('date_of_birthday'), '%Y-%m-%d')
            if not user.get('avatar') == 'None':
                obj.avatar = user.get('avatar')
            if not user.get('phone') == 'None':
                obj.phone = user.get('phone')
                obj.save()

            user['obj'] = obj
        return users

    @staticmethod
    def create_company(users):
        owner = None
        for user in users:
            if user.get('id') == '173':
                owner = user.get('obj')
        company = company_models.Company.objects.create(
            owner=owner,
            is_activate=True,
            name='Landskap',
            logo='snFF7X9EvEc.jpg',
        )
        return company

    @staticmethod
    def create_cafes(company):
        cafes = get_data('export/cafe')
        save_cafes = list()
        for cafe in cafes:
            if not cafe.get('company') == '3':
                continue
            obj = company_models.Cafe()
            obj.logo = cafe.get('cafe_logo')
            obj.name = cafe.get('cafe_name')
            obj.description = cafe.get('description')
            obj.call_center = cafe.get('call_center')
            obj.website = cafe.get('website')
            obj.status = bool(int(cafe.get('status')))
            obj.location = get_gio_cafe(cafe.get('id'))
            obj.address = cafe.get('address')
            obj.second_address = cafe.get('second_address')
            obj.postal_code = cafe.get('postal_code')
            obj.tax_rate = float(cafe.get('tax_rate'))
            obj.cafe_timezone = cafe.get('cafe_timezone')
            obj.delivery_available = bool(int(cafe.get('delivery_available')))
            obj.delivery_max_distance = int(cafe.get('delivery_max_distance'))
            obj.delivery_min_amount = float(cafe.get('delivery_min_amount'))
            obj.delivery_fee = float(cafe.get('delivery_fee'))
            obj.delivery_percent = float(cafe.get('delivery_percent'))
            obj.delivery_km_amount = float(cafe.get('delivery_km_amount'))
            obj.delivery_min_time = int(cafe.get('delivery_min_time'))
            obj.version = int(cafe.get('version'))
            obj.order_limit = int(cafe.get('order_limit'))
            obj.order_time_limit = int(cafe.get('order_time_limit'))
            obj.company = company
            obj.save()
            cafe['obj'] = obj
            save_cafes.append(cafe)
        return save_cafes

    @staticmethod
    def create_menu(cafes: list, company) -> list:
        for cafe in cafes:
            cafe_obj = cafe.get('obj')
            menu = company_models.Menu()
            menu.company = company
            menu.name = f'{cafe_obj.name} Menu'
            menu.save()
            menu.cafes.add(cafe_obj)
            cafe['menu'] = menu
        return cafes

    # @staticmethod
    # def create_category(cafes: list) -> list:
    #     for cafe in cafes:
    #         cafe_id = cafe.get('id')
    #         cafe_obj = cafe.get('obj')
    #         cafe_owner = cafe.get('owner')
    #         menu = cafe.get('menu')
    #         categories = get_product_categories(cafe.get('user'))
    #         for c in categories:  # CREATE CATEGORY
    #             obj = product_models.ProductCategory()
    #             obj.menu = menu
    #             obj.name = c.get('name')
    #             obj.image = c.get('icon')
    #             obj.available = bool(int(c.get('available')))
    #             obj.position = int(c.get('order'))
    #             obj.save()
    #             c['obj'] = obj
    #         for c in categories:  # ADD CATEGORY PARENT
    #             if not c.get('parent') == 'None':
    #                 parent = get_category_parent(categories, c.get('parent'))
    #                 child = c.get('obj')
    #                 if parent:
    #                     child.parent = parent.get('obj')
    #                     child.save()
    #
    #         cafe['categories'] = categories
    #     return cafes
    #
    # @staticmethod
    # def create_products(cafes: list) -> list:
    #     for cafe in cafes:
    #         categories = cafe.get('categories')
    #         if categories:
    #             for category in categories:
    #                 products = get_products(cafe.get('id'), category.get('id'))
    #                 if products:
    #                     for product in products:
    #                         obj = create_product(product, category.get('obj'))
    #                         product['obj'] = obj
    #
    #                     category['products'] = products
    #
    #     return cafes

    @staticmethod
    def create_cafe_products(cafes: list):
        for cafe in cafes:
            menu = cafe.get('menu')
            cafe_id = cafe.get('id')
            product_list = get_cafe_product_list(cafe_id)
            parent = None
            sub_category = None
            cafe_products = list()
            for p in product_list:

                if p.get('type') == 0:
                    p = create_category(p.get('category'), menu)
                    parent = p.get('obj')
                    d = {
                        'type': 'category',
                        'obj': parent,
                        'id': p.get('category')
                    }
                    cafe_products.append(d)

                if p.get('type') == 1:
                    s = create_category(p.get('subcategory'), menu)
                    sub_category = s.get('obj')
                    sub_category.parent = parent
                    sub_category.save()
                    d = {
                        'type': 'category',
                        'obj': sub_category,
                        'id': s.get('category')
                    }
                if p.get('type') == 2:
                    s = create_products(p.get('products'), sub_category)
                    d = {
                        'type': 'products',
                        'obj': s,
                    }
            cafe['products'] = cafe_products
        return cafes






