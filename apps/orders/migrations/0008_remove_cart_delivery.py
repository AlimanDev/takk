# Generated by Django 3.2.2 on 2021-06-07 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_cart_cartitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='delivery',
        ),
    ]