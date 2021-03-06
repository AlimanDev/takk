# Generated by Django 3.2.2 on 2021-05-26 08:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0007_auto_20210526_0642'),
        ('products', '0006_auto_20210526_0608'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('points', models.PositiveIntegerField(default=1)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'points',
            },
        ),
        migrations.CreateModel(
            name='FreeItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expiration_days', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('valid', 'Valid'), ('expired', 'Expired'), ('redeemed', 'Redeemed')], default='valid', max_length=60)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.company')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='free_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'free_item',
            },
        ),
    ]
