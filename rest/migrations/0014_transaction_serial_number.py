# Generated by Django 4.1.7 on 2024-09-16 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0013_remove_transaction_buyer_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='serial_number',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
