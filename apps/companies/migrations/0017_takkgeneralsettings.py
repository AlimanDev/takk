# Generated by Django 3.2.2 on 2021-07-02 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0016_companycard'),
    ]

    operations = [
        migrations.CreateModel(
            name='TakkGeneralSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cashback', models.DecimalField(decimal_places=2, default=5, max_digits=5)),
                ('updated_dt', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
