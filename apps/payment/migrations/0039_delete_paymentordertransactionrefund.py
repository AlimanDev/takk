# Generated by Django 3.2.2 on 2021-07-25 07:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0038_auto_20210725_0655'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PaymentOrderTransactionRefund',
        ),
    ]
