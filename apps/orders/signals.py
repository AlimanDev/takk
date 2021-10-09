from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders import models as order_models


# @receiver(signal=post_save, sender=order_models.Order)
# def department_update(sender, instance, created, **kwargs):
#
#     if not created and instance.status == order_models.Order.PAID and not instance.is_comfirm:
#         pass

