# Generated by Django 3.2.2 on 2021-06-09 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0008_alter_cafe_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cafe',
            name='menu',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafes', to='companies.menu'),
        ),
    ]
