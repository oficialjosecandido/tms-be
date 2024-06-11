# Generated by Django 4.1.7 on 2024-06-10 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0009_listing_other_accessories_listing_other_condition_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='location_zipcode',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='queue_order',
            field=models.CharField(blank=True, choices=[('TMS', 'TMS'), ('Promoted)', 'Promoted'), ('Normal', 'Normal)')], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='shoes_size',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
