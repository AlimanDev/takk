# Generated by Django 3.2.2 on 2021-07-11 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0018_customercard_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stripeinvoicetransactions',
            name='user',
        ),
        migrations.DeleteModel(
            name='StripeInvoiceItemTransactions',
        ),
        migrations.DeleteModel(
            name='StripeInvoiceTransactions',
        ),
    ]
