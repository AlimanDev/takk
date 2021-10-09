# Generated by Django 3.2.2 on 2021-07-17 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_auto_20210716_1524'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='is_free',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='free_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]