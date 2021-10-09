# Generated by Django 3.2.2 on 2021-05-20 14:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='employee',
            name='notification_cafes',
            field=models.ManyToManyField(blank=True, related_name='employees_notification', to='companies.Cafe'),
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='company',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Company owner'),
        ),
        migrations.AddField(
            model_name='cafeweektime',
            name='cafe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='week_time', to='companies.cafe'),
        ),
        migrations.AddField(
            model_name='cafephoto',
            name='cafe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='companies.cafe'),
        ),
        migrations.AddField(
            model_name='cafe',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cafes', to='companies.company'),
        ),
        migrations.AddField(
            model_name='cafe',
            name='menu',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafes', to='companies.menu'),
        ),
    ]