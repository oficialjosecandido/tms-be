# Generated by Django 4.1.7 on 2024-09-03 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0003_alter_listingimage_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='listing',
        ),
        migrations.DeleteModel(
            name='File',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
