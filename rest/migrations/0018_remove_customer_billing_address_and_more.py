# Generated by Django 4.1.7 on 2024-07-17 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0017_remove_customer_profile_picture_customer_valid_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='billing_address',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='shipping_address',
        ),
    ]
