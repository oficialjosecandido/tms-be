# Generated by Django 4.1.7 on 2024-09-05 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0009_alter_listing_condition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='status',
            field=models.CharField(blank=True, default='Active', max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='status',
            field=models.CharField(choices=[('Pending Confirmation', 'Pending Confirmation'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Closed', 'Closed'), ('Pending Payment', 'Pending Payment'), ('Sold', 'Sold')], default='Approved', max_length=200),
        ),
    ]
