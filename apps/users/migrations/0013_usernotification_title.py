# Generated by Django 3.2.2 on 2021-09-07 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_alter_usernotification_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotification',
            name='title',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
