# Generated by Django 3.2.2 on 2021-10-05 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0029_alter_company_validity_point_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='takkfeeforcompany',
            name='fee_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]