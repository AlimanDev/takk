# Generated by Django 3.2.2 on 2021-07-11 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0019_takkgeneralsettings_charge_limit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='takkgeneralsettings',
            name='charge_limit',
            field=models.IntegerField(default=2500),
        ),
    ]
