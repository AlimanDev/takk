# Generated by Django 3.2.2 on 2021-06-10 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_product_quickest_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productcategory',
            options={'ordering': ('-id',), 'verbose_name': 'Product Category', 'verbose_name_plural': 'Product Categories'},
        ),
    ]
