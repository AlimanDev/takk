# Generated by Django 3.2.2 on 2021-07-16 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_auto_20210716_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='tip',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='cart',
            name='tip_percent',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
