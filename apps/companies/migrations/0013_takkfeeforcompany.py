# Generated by Django 3.2.2 on 2021-06-26 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_alter_cafe_menu'),
    ]

    operations = [
        migrations.CreateModel(
            name='TakkFeeForCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_percent', models.BooleanField(default=False)),
                ('fee_percent', models.SmallIntegerField(blank=True, null=True)),
                ('fee_amount', models.IntegerField(blank=True, null=True)),
                ('created_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company')),
            ],
            options={
                'db_table': 'takk_fee_for_company',
            },
        ),
    ]
