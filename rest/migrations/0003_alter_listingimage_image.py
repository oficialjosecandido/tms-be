# Generated by Django 4.1.7 on 2024-09-03 10:36

from django.db import migrations, models
import rest.models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0002_file_transaction_rename_bid_date_bid_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listingimage',
            name='image',
            field=models.ImageField(upload_to=rest.models.ListingImage.get_upload_path),
        ),
    ]
