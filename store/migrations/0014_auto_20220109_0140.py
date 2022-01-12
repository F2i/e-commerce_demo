# Generated by Django 3.2.7 on 2022-01-08 18:40

from django.db import migrations, models
import store.models
import store.validators


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_productimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='promotions',
            field=models.ManyToManyField(null=True, to='store.Promotion'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.FileField(upload_to=store.models.ProductImage.Utils.get_product_title, validators=[store.validators.FileSizeValidator(max_file_size_mb=1)]),
        ),
    ]
