# Generated by Django 3.2.2 on 2021-09-18 03:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0034_alter_orderitem_free_price'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-created',)},
        ),
    ]