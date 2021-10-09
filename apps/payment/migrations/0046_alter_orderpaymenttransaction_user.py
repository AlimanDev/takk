# Generated by Django 3.2.2 on 2021-09-16 16:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0045_alter_stripecustomer_customer_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderpaymenttransaction',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_transactions', to=settings.AUTH_USER_MODEL),
        ),
    ]