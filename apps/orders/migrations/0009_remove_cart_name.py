# Generated by Django 3.2.2 on 2021-06-07 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_remove_cart_delivery'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='name',
        ),
    ]