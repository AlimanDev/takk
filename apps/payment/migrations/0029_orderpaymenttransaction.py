# Generated by Django 3.2.2 on 2021-07-23 08:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0020_alter_takkgeneralsettings_charge_limit'),
        ('orders', '0024_remove_cartitem_is_free'),
        ('payment', '0028_remove_budgettransaction_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderPaymentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=250, null=True)),
                ('amount', models.IntegerField()),
                ('cashback', models.IntegerField(default=0)),
                ('payment_type', models.SmallIntegerField(choices=[(0, 'Online payment'), (1, 'Balance payment')])),
                ('created_dt', models.DateTimeField(auto_now_add=True)),
                ('updated_dt', models.DateTimeField(auto_now=True)),
                ('status', models.SmallIntegerField(choices=[(0, 'Paid'), (1, 'Refund')], default=0)),
                ('cafe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='companies.cafe')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.order')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'order_payment_transactions',
            },
        ),
    ]
