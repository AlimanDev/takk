# Generated by Django 3.2.2 on 2021-05-20 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_alter_menu_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cafe',
            name='state',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
