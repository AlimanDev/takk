# Generated by Django 3.2.2 on 2021-07-23 09:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0024_remove_cartitem_is_free'),
        ('companies', '0020_alter_takkgeneralsettings_charge_limit'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0031_alter_orderpaymenttransaction_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentOrderTransactionRefund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('created_dt', models.DateTimeField(auto_now_add=True)),
                ('updated_dt', models.DateTimeField(auto_now=True)),
                ('is_refund', models.BooleanField(default=True)),
                ('cafe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='companies.cafe')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.order')),
                ('order_items', models.ManyToManyField(blank=True, to='orders.OrderItem')),
                ('transaction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payment.orderpaymenttransaction')),
            ],
            options={
                'db_table': 'payment_order_transaction_refund',
                'ordering': ('-created_dt',),
            },
        ),
    ]
