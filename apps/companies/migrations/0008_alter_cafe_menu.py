# Generated by Django 3.2.2 on 2021-06-09 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0007_auto_20210526_0642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cafe',
            name='menu',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafe', to='companies.menu'),
        ),
    ]
