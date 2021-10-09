# Generated by Django 3.2.2 on 2021-05-22 05:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_alter_cafe_state'),
        ('products', '0003_alter_product_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modifier',
            name='cafe',
        ),
        migrations.AddField(
            model_name='modifier',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
            preserve_default=False,
        ),
    ]
