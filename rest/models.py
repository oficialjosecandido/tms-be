# myapp/models.py
from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime
import os
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
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    vat = models.CharField(max_length=20, blank=True, null=True)
    balance = models.IntegerField(default=0, null=True, blank=True)
    trusted_buyer = models.BooleanField(default=False)
    trusted_seller = models.BooleanField(default=False)
    rating = models.IntegerField(default=0, null=True, blank=True)

    address1 = models.CharField(max_length=200, blank=True, null=True)
    address2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=150, blank=True, null=True, default='Waiting 3rd Party Activation')
    image = models.FileField(upload_to='listing_images/', blank=True, null=True)
    valid_id = models.BooleanField(default=False)

    language = models.CharField(max_length=5, null=True, blank=True)
    currency = models.CharField(max_length=5, null=True, blank=True)

    def save_images(self, images):
        for index, image in enumerate(images):
            file_name = f"customer_{self.id}_id_{index + 1}.jpg" 
            self.image.save(file_name, image, save=False)
        self.save()

    def __str__(self):
        return f"{self.display_name} - {self.email} was created by {self.created_date} and has a status of {self.status}"


class File(models.Model):
    file = models.FileField(upload_to='uploads/')

class Listing(models.Model):
    STATUS_CHOICES = [
        ('Pending Confirmation', 'Pending Confirmation'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Pending Payment', 'Pending Payment'),
        ('Sold', 'Sold'),
    ]

    CONDITION_CHOICES = [
        ('A', 'A'),
        ('B', 'B)'),
        ('C', 'C'),
        ('D', 'D')
    ]

    title = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=200, null=True, blank=True)

    brand = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Pending Confirmation')
    created_at = models.DateTimeField(auto_now_add=True)

    buynow_price = models.IntegerField(default=0, null=True, blank=True)
    starting_price = models.IntegerField(default=0, null=True, blank=True)

    condition = models.CharField(max_length=100, choices=CONDITION_CHOICES, blank=True, null=True)
    excerpt = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    promoted = models.BooleanField(null=True, blank=True, default=False)
    

    location_address1 = models.CharField(max_length=200, null=True, blank=True)
    location_address2 = models.CharField(max_length=100, null=True, blank=True)
    location_city = models.CharField(max_length=100, null=True, blank=True)
    location_zipcode = models.CharField(max_length=100, null=True, blank=True)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    image = models.ImageField(upload_to='listing_images/')  # Files will be stored in `listing_images/` folder in S3


    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            today_str = datetime.today().strftime('%Y%m%d')
            base_slug = slugify(self.title)
            self.slug = f'{base_slug}-{today_str}'

            # Check if the slug is unique and adjust if necessary
            existing_slugs = Listing.objects.filter(slug__startswith=self.slug).count()
            if existing_slugs:
                self.slug = f'{self.slug}-{existing_slugs + 1}'

        super(Listing, self).save(*args, **kwargs)

    def __str__(self):
        return f'Listing ID: {self.id} with price {self.starting_price}, Customer: {self.customer.display_name}'


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing_images')
    image = models.ImageField(upload_to='listing_images/')

    def __str__(self):
        return f'Image for Listing ID: {self.listing.id}'

class Bid(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Rejected', 'Rejected'),
        ('Accepted', 'Accepted'),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bid')
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bid = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f'New bid on listing: {self.listing.slug} with bid {self.bid} by customer: {self.customer.display_name} with status {self.status}'

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('Payment Initiated', 'Payment Initiated'),
        ('Payment on Hold', 'Payment on Hold'),
        ('Payout Completed', 'Payout Completed'),
    ]

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

    items = models.CharField(max_length=200, blank=True, null=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return f'Transaction ID: {self.id} with seller: {self.seller_name} and buyer: {self.buyer_name} with status: {self.status} for {self.amount}'


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.name} on listing nº {self.listing.id}'







