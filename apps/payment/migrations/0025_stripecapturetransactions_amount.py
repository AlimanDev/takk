# Generated by Django 3.2.2 on 2021-07-13 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0024_auto_20210713_0922'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripecapturetransactions',
            name='amount',
            field=models.IntegerField(null=True),
        ),
    ]
