# Generated by Django 3.2.2 on 2021-09-07 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0032_orderitem_is_ready'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_acknowledge',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
