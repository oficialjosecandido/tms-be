# Generated by Django 4.1.7 on 2024-07-11 22:23

from django.db import migrations, models
import rest.models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0014_customer_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='address1',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='address2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='city',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='zipcode',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to=rest.models.customer_id_upload_path),
        ),
    ]
