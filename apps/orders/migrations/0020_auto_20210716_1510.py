# Generated by Django 3.2.2 on 2021-07-16 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0019_cartitem_is_free'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='pre_order',
        ),
        migrations.AddField(
            model_name='order',
            name='free_items',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
