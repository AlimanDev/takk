# Generated by Django 3.2.2 on 2021-08-13 05:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0041_auto_20210726_0510'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stripechargetransaction',
            name='card',
        ),
        migrations.RemoveField(
            model_name='stripechargetransaction',
            name='order',
        ),
        migrations.RemoveField(
            model_name='stripechargetransaction',
            name='user',
        ),
        migrations.DeleteModel(
            name='StripeCaptureTransactions',
        ),
        migrations.DeleteModel(
            name='StripeChargeTransaction',
        ),
    ]
