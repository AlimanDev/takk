# Generated by Django 3.2.2 on 2021-07-02 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0014_alter_stripewebhookevent_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgettransaction',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'In process'), (1, 'Succeeded'), (2, 'Failed')], default=0),
        ),
    ]