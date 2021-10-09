# Generated by Django 3.2.2 on 2021-06-29 13:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_rename_expiration_days_freeitem_expiration_dt'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0004_alter_stripetransaction_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=250)),
                ('amount_payout', models.IntegerField()),
                ('amount_receipt', models.IntegerField()),
                ('status', models.SmallIntegerField(choices=[(0, 'In process'), (1, 'Succeeded'), (2, 'Failed')], default=0)),
                ('created_dt', models.DateTimeField(auto_now_add=True)),
                ('updated_dt', models.DateTimeField(auto_now=True)),
                ('tariff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.budgettariff')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'budget_transactions',
                'ordering': ('-created_dt',),
            },
        ),
    ]