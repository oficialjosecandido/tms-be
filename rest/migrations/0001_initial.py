# Generated by Django 4.1.7 on 2025-03-14 23:44

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import rest.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(blank=True, max_length=500, null=True)),
                ('email', models.CharField(max_length=500)),
                ('phone_number', models.CharField(blank=True, max_length=100, null=True)),
                ('vat', models.CharField(blank=True, max_length=20, null=True)),
                ('frozen_deposit', models.IntegerField(blank=True, default=0, null=True)),
                ('free_deposit', models.IntegerField(blank=True, default=0, null=True)),
                ('level', models.CharField(blank=True, choices=[('Platinum', 'Platinum'), ('Gold', 'Gold'), ('Silver', 'Silver'), ('Bronze', 'Bronze'), ('Grass', 'Grass')], max_length=20, null=True)),
                ('rating', models.IntegerField(blank=True, default=0, null=True)),
                ('verified', models.BooleanField(blank=True, default=False, null=True)),
                ('address1', models.CharField(blank=True, max_length=200, null=True)),
                ('address2', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=20, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(blank=True, default='Active', max_length=150, null=True)),
                ('valid_id', models.BooleanField(default=False)),
                ('language', models.CharField(blank=True, default='en', max_length=5, null=True)),
                ('currency', models.CharField(blank=True, default='eur', max_length=5, null=True)),
                ('image', models.ImageField(upload_to=rest.models.Customer.get_upload_path)),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True)),
                ('brand', models.CharField(blank=True, max_length=100, null=True)),
                ('category', models.CharField(choices=[('Cars', 'Cars'), ('Motos', 'Motos'), ('Boats', 'Boats'), ('Tech', 'Tech'), ('Fashion', 'Fashion'), ('Furniture', 'Furniture'), ('Art & Deco', 'Art & Deco'), ('Jewelry', 'Jewelry'), ('Sports', 'Sports'), ('Real Estate', 'Real Estate'), ('Lifestyle', 'Lifestyle'), ('Apparel', 'Apparel'), ('Kids', 'Kids'), ('Gaming', 'Gaming')], max_length=100)),
                ('status', models.CharField(choices=[('Pending Confirmation', 'Pending Confirmation'), ('Active', 'Active'), ('Rejected', 'Rejected'), ('Closed', 'Closed'), ('On hold', 'On hold'), ('Pending Payment', 'Pending Payment'), ('Sold', 'Sold')], default='Active', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('close_date', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('buynow_price', models.IntegerField(blank=True, default=0, null=True)),
                ('starting_price', models.IntegerField(blank=True, default=0, null=True)),
                ('condition', models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=100, null=True)),
                ('excerpt', models.CharField(blank=True, max_length=300, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('level', models.IntegerField(blank=True, choices=[('Platinum', 'Platinum'), ('Gold', 'Gold'), ('Silver', 'Silver'), ('Bronze', 'Bronze'), ('Grass', 'Grass')], null=True)),
                ('duration', models.CharField(blank=True, max_length=100, null=True)),
                ('promoted', models.BooleanField(blank=True, default=False, null=True)),
                ('location_address1', models.CharField(blank=True, max_length=200, null=True)),
                ('location_address2', models.CharField(blank=True, max_length=100, null=True)),
                ('location_city', models.CharField(blank=True, max_length=100, null=True)),
                ('location_zipcode', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(upload_to='listing_images/')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(blank=True, max_length=200, null=True)),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Waiting Payment/Delivery', 'Waiting Payment/Delivery'), ('Transaction completed', 'Transaction Completed'), ('Transaction on Dispute', 'Transaction on Dispute'), ('Transaction Canceled', 'Transaction Canceled')], default='Waiting Payment/Delivery', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('delivered', models.BooleanField(blank=True, default=False, null=True)),
                ('paid', models.BooleanField(blank=True, default=False, null=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer', to='rest.customer')),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='rest.listing')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller', to='rest.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Stripe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(choices=[('Add', 'Add'), ('Withdraw', 'Withdraw')], default='Withdraw', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest.customer')),
            ],
        ),
        migrations.CreateModel(
            name='ListingImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=rest.models.get_listing_upload_path)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listing_images', to='rest.listing')),
            ],
        ),
        migrations.CreateModel(
            name='Dispute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Dispute Initiated', 'Dispute Initiated'), ('Dispute in Analysis', 'Dispute in Analysis'), ('Resolved for Buyer', 'Resolved for Buyer'), ('Resolved for Seller', 'Resolved for Seller')], default='Dispute Initiated', max_length=200)),
                ('message', models.TextField(blank=True, null=True)),
                ('persona', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_disputed', to='rest.customer')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_disputed', to='rest.customer')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='rest.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('points', models.IntegerField(default=0)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='customuser_groups_set', related_query_name='user', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='customuser_permissions_set', related_query_name='user', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('bid', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Rejected', 'Rejected'), ('Accepted', 'Accepted')], default='Active', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest.customer')),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bid', to='rest.listing')),
            ],
        ),
    ]
