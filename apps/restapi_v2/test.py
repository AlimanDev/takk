import datetime

# LIBS
import stripe
from django.db.models import QuerySet, Prefetch
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework_tracking.mixins import LoggingMixin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

# DJANGO
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.conf import settings
from django.utils.decorators import method_decorator

# APPS
from apps.restapi_v2 import serializers as restapi_v2_serializers
from apps.restapi_v2 import logics as restapi_v2_logics
from apps.restapi_v2 import tasks as restapi_v2_tasks
from apps.restapi_v2.mobile import serializers as mobile_serializers
from apps.restapi_v2.mobile import logics as mobile_logics
from apps.restapi_v2.paginations import MobilePagination

from apps.users import models as user_models
from apps.payment.logic import balance as balance_payment_logics
from apps.payment import models as payment_models
from apps.companies import models as company_models
from apps.orders import models as order_models
from apps.restapi_v2 import permissions as restapi_permissions
from apps.products import models as product_models
from django.db import connection, reset_queries
import time
import functools


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return 'end'

    return inner_func


@query_debugger
def test():
    cafe = company_models.Cafe.objects.get(id=10)
    not_available_product_ids = product_models.CafeProductState.objects.filter(
                cafe_id=cafe.id).values_list('product_id', flat=True)
    # print(not_available_product_ids)
    categories = product_models.ProductCategory.objects.prefetch_related('children').prefetch_related(
        Prefetch('products', product_models.Product.objects.select_related('category').prefetch_related('sizes').
                 prefetch_related(
            Prefetch('modifiers', product_models.Modifier.objects.prefetch_related('items').all())).all())).filter(
        menu_id=cafe.menu_id)
    context = {'cafe': cafe, 'not_available_product_ids': not_available_product_ids}
    categories_header = categories.filter(parent__isnull=True)
    ready_list = list()  # Список всех товаров
    categories_header_serializer = mobile_serializers.ProductCategorySerializer(
        categories_header, context=context, many=True).data

    for category in categories_header:  # Все категории продуктов (parent == null)
        ready_list.append({
            'type': 0,
            'category': mobile_serializers.ProductCategorySerializer(
                category, context=context).data})
        if category.products.exists():
            ready_list.append({
                        'type': 2,
                        'products': mobile_serializers.ProductSerializer(
                            category.products.all(), context=context, many=True).data})

        if category.children.all():  # Если есть subcategory
            for subcategory in category.children.all():
                ready_list.append({
                    'type': 0,
                    'subcategory': mobile_serializers.ProductCategorySerializer(
                        subcategory, context=context).data})
                if subcategory.products.exists():
                    ready_list.append({
                        'type': 2,
                        'products': mobile_serializers.ProductSerializer(
                            subcategory.products.all(), context=context, many=True).data})
    result = {
        'version': cafe.version,
        'categories': categories_header_serializer,
        'list': ready_list
    }
    return str()
