# Generated by Django 3.2.2 on 2021-07-12 11:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0022_auto_20210712_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripechargetransaction',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='charge_transactions', to=settings.AUTH_USER_MODEL),
        ),
    ]
