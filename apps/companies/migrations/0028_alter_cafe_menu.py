# Generated by Django 3.2.2 on 2021-09-01 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0027_auto_20210828_0551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cafe',
            name='menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafes', to='companies.menu'),
        ),
    ]