# Generated by Django 3.2.2 on 2021-06-10 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_alter_cafe_menu'),
        ('orders', '0010_auto_20210609_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='cafe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cafes', to='companies.cafe'),
        ),
    ]
