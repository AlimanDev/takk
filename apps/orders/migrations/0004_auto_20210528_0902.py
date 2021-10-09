# Generated by Django 3.2.2 on 2021-05-28 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20210527_1340'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='tax',
        ),
        migrations.AddField(
            model_name='favoritecart',
            name='delivery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.delivery'),
        ),
        migrations.AddField(
            model_name='favoritecartitem',
            name='instruction',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='favoritecartitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='free_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='instruction',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='is_free',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='tax_percent',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='tax_rate',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=100),
        ),
    ]
