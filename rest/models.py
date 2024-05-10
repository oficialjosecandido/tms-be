# myapp/models.py
from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

def customer_image_upload_path(instance, filename):
    # Get the customer's email
        customer_email = instance.customer.email
        # Replace special characters in the email to create a valid folder name
        folder_name = customer_email.replace('@', '_').replace('.', '_')
        # Construct the file path
        return os.path.join('customer_images', folder_name, filename)

class CustomUser(AbstractUser):
    # Your custom user model fields go here
    points = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    # Use unique related_name for each field
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups_set',
        related_query_name='user',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        related_query_name='user',
        blank=True,
        help_text='Specific permissions for this user.',
    )

class Customer(models.Model):
    display_name = models.CharField(max_length=500, blank=True, null=True)
    email = models.CharField(max_length=500)
    # id_number = models.CharField(max_length=500, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    balance = models.IntegerField(default=0, null=True, blank=True)
    trusted_buyer = models.BooleanField(default=False)
    trusted_seller = models.BooleanField(default=False)
    buyer_stars = models.IntegerField(default=0, null=True, blank=True)
    seller_stars = models.IntegerField(default=0, null=True, blank=True)
    billing_address = models.TextField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    profile_picture = models.FileField(upload_to='profiles/', blank=True, null=True)
    # id_file = models.FileField(upload_to='ids/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=150, blank=True, null=True, default='Waiting 3rd Party Activation')

    def __str__(self):
        return f"{self.display_name} - {self.email} was created by {self.created_date} and has a status of {self.status}"


class Listing(models.Model):
    STATUS_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Pending Pickup', 'Pending Pickup'),
        ('Pending Delivery', 'Pending Delivery'),
        ('Delivered', 'Deliver'),
        ('Sold', 'Sold'),
    ]

    BUY_DATE_CHOICES = [
        ('Before 2018', 'Before 2018'),
        ('2018 - 2020', '2018 - 2020'),
        ('2021 - 2022', '2021 - 2022'),
        ('2023 to present', '2023 to present')
    ]

    CONDITION_CHOICES = [
        ('Needs some love', 'Needs some love'),
        ('Works well (201-500 Rides)', 'Works well (201-500 Rides)'),
        ('Very good (51-200 Rides)', 'Very good (51-200 Rides)'),
        ('Excellent (0 - 50 Rides)', 'Excellent (0 - 50 Rides)')
    ]

    buy_date = models.CharField(max_length=100, choices=BUY_DATE_CHOICES, blank=True, null=True)
    bike_condition = models.CharField(max_length=100, choices=CONDITION_CHOICES, blank=True, null=True)

    bike_options = models.JSONField()
    bike_accessories = models.JSONField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Approved')
    created_at = models.DateTimeField(auto_now_add=True)
    asking_price = models.IntegerField(default=0, null=True, blank=True)
    image = models.FileField(upload_to=customer_image_upload_path, blank=True, null=True)

    

    def __str__(self):
        return f'Listing ID: {self.id} with price {self.asking_price}, Customer: {self.customer.display_name}'


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Done', 'Done'),
        ('Rejected', 'Rejected'),
    ]

    listing_id = models.IntegerField()
    amount = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Seller information
    seller_name = models.CharField(max_length=100)
    seller_email = models.EmailField()
    seller_phone_number = models.CharField(max_length=20)
    
    # Buyer information
    buyer_name = models.CharField(max_length=100)
    buyer_email = models.EmailField()
    buyer_phone_number = models.CharField(max_length=20)
    
    def __str__(self):
        return f'Transaction ID: {self.id} for Listing ID: {self.listing_id}'

class Bid(models.Model):
    bidprice = models.DecimalField(max_digits=10, decimal_places=2)
    biduser = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    bidlisting = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Bid for {self.bidlisting.title} by {self.biduser.username} at {self.bidprice}"
