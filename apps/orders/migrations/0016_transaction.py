# Generated by Django 3.2.2 on 2021-06-22 16:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_alter_cafe_menu'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0015_auto_20210622_1332'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_dt', models.DateTimeField(auto_now=True)),
                ('amount', models.FloatField(null=True)),
                ('payment_type', models.CharField(max_length=254, null=True)),
                ('last_digits', models.CharField(max_length=24, null=True)),
                ('meta', models.CharField(max_length=254, null=True)),
                ('cashback', models.FloatField(default=0)),
                ('is_batch', models.BooleanField(default=False)),
                ('cafe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='companies.cafe')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transaction', to='orders.order')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'transaction',
                'ordering': ['-created_dt'],
            },
        ),
    ]
