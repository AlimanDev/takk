# Generated by Django 3.2.2 on 2021-06-19 15:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_cart_cafe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='customer',
            new_name='user',
        ),
    ]
