# Generated by Django 3.2.2 on 2021-07-13 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0025_stripecapturetransactions_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stripechargetransaction',
            old_name='is_capture',
            new_name='is_cancel',
        ),
    ]
