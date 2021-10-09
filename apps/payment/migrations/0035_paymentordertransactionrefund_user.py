# Generated by Django 3.2.2 on 2021-07-23 13:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0034_auto_20210723_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentordertransactionrefund',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cancel_orders', to=settings.AUTH_USER_MODEL),
        ),
    ]