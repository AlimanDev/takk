# Generated by Django 3.2.2 on 2021-08-12 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0020_alter_takkgeneralsettings_charge_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='about',
            field=models.CharField(blank=True, max_length=1500, null=True),
        ),
    ]