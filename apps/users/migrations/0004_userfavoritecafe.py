# Generated by Django 3.2.2 on 2021-06-10 16:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_alter_cafe_menu'),
        ('users', '0003_alter_user_mobile_os'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFavoriteCafe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cafes', models.ManyToManyField(blank=True, to='companies.Cafe')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_cafes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
