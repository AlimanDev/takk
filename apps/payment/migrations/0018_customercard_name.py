# Generated by Django 3.2.2 on 2021-07-11 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0017_customercard'),
    ]

    operations = [
        migrations.AddField(
            model_name='customercard',
            name='name',
            field=models.CharField(max_length=250, null=True),
        ),
    ]