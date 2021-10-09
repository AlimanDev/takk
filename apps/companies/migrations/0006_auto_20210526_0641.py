# Generated by Django 3.2.2 on 2021-05-26 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20210526_0608'),
        ('companies', '0005_alter_employee_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='cafe',
            name='exchangeable_point',
            field=models.IntegerField(default=10),
        ),
        migrations.AddField(
            model_name='cafe',
            name='exchangeable_products',
            field=models.ManyToManyField(blank=True, related_name='exchangeable_products', to='products.ProductCategory'),
        ),
        migrations.AddField(
            model_name='cafe',
            name='expiration_days',
            field=models.IntegerField(default=30),
        ),
        migrations.AddField(
            model_name='cafe',
            name='give_points',
            field=models.ManyToManyField(blank=True, to='products.ProductCategory'),
        ),
    ]
