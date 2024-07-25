# Generated by Django 4.1.7 on 2024-07-24 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0019_customer_currency_customer_language'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='model',
            new_name='brand',
        ),
        migrations.RenameField(
            model_name='listing',
            old_name='image',
            new_name='images',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='bike_accessories',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='bike_condition',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='bike_options',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='buy_date',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='other_accessories',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='other_condition',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='queue_order',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='serial_number',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='shoes_size',
        ),
        migrations.AddField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='condition',
            field=models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B)'), ('C', 'C'), ('D', 'D')], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='location_address1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='location_address2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='location_city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='status',
            field=models.CharField(choices=[('Pending Confirmation', 'Pending Confirmation'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Pending Payment', 'Pending Payment'), ('Sold', 'Sold')], default='Pending Confirmation', max_length=20),
        ),
    ]
