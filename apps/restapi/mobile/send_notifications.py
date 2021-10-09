import pdb
from rest_framework.exceptions import APIException, ValidationError, NotFound
from apps.companies import models as company_models
from django.http import HttpResponse
import stripe
import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.orders import models as order_models
from apps.payment import models as payment_models
from apps.users import models as user_models
from apps.restapi.mobile import serializer_logics
from apps.restapi import tasks
from apps.payment.logic import logics as payment_logics

######################
# USER NOTIFICATIONS #
######################


def user_give_cashback():
    pass


def user_order_acknowledge(order: order_models.Order) -> None:
    try:
        title = 'You order cafe: {} order: {} acknowledge'.format(order.cafe.name, order.pk)
        body = 'TEST BODY ORDER ACKNOWLEDGE'
        tasks.send_notification.delay(order.user.id, title, body)
    except Exception as e:
        print(str(e))


def user_order_refund():
    pass


def user_order_ready():
    pass


def user_give_points():
    pass


def user_give_free_item():
    pass

#########################
# EMPLOYEE NOTIFICATION #
#########################


def employee_new_order(order: order_models.Order):
    try:
        title = 'New order cafe: {} order: {}'.format(order.cafe.name, order.pk)
        body = 'TEST BODY'
        employees = order.cafe.get_employees()
        if employees.exists():
            for employee in employees:
                tasks.send_notification.delay(employee.user.id, title, body)
    except Exception as e:
        print(str(e))


def employee_order_item_ready():
    pass

############################
# TAKK OWNER NOTIFICATION  #
############################