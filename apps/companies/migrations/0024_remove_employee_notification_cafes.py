# Generated by Django 3.2.2 on 2021-08-13 04:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0023_auto_20210813_0446'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='notification_cafes',
        ),
    ]
