# Generated by Django 3.2.2 on 2021-08-13 05:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0029_alter_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='is_confirm',
        ),
    ]