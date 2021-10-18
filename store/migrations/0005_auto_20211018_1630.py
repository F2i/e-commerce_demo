# Generated by Django 3.2.7 on 2021-10-18 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_adress_zip'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['last_name', 'first_name'], name='store_custo_last_na_e6a359_idx'),
        ),
        migrations.AlterModelTable(
            name='customer',
            table='store_customers',
        ),
    ]
