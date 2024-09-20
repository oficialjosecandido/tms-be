# myapp/models.py
from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime, timedelta
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
    status = models.CharField(max_length=150, blank=True, null=True, default='Active')
    image = models.FileField(upload_to='disposable_info/', blank=True, null=True)
    valid_id = models.BooleanField(default=False)

    language = models.CharField(max_length=5, null=True, blank=True, default='EN')
    currency = models.CharField(max_length=5, null=True, blank=True)

    def save_images(self, images):
        for index, image in enumerate(images):
            file_name = f"customer_{self.id}_id_{index + 1}.jpg" 
            self.image.save(file_name, image, save=False)
        self.save()


    def get_upload_path(instance, filename):
        """
        Function to determine the upload path dynamically.
        Saves files to: auctions/customer_email/listing_id/filename
        """
        
        return os.path.join('customers', instance.email, filename)

    image = models.ImageField(upload_to=get_upload_path)

    def __str__(self):
        return f"{self.display_name} - {self.email} was created by {self.created_date} and has a status of {self.status}"

class Listing(models.Model):

    CATEGORIES = [
        ('Cars', 'Cars'),
        ('Motos', 'Motos'),
        ('Boats', 'Boats'),
        ('Tech', 'Tech'),
        ('Fashion', 'Fashion'),
        ('Furniture', 'Furniture'),
        ('Art & Deco', 'Art & Deco'),
        ('Jewelry', 'Jewelry'),
        ('Sports', 'Sports'),
        ('Real Estate', 'Real Estate'),
        ('Lifestyle', 'Lifestyle'),
        ('Apparel', 'Apparel'),
        ('Kids', 'Kids'),
        ('Gaming', 'Gaming'),
    ]

    STATUS_CHOICES = [
        ('Pending Confirmation', 'Pending Confirmation'),
        ('Active', 'Active'),
        ('Rejected', 'Rejected'),
        ('Closed', 'Closed'),
        ('On hold', 'On hold'), #If no offer was accepted and listing was closed 48h ago
        ('Pending Payment', 'Pending Payment'),
        ('Sold', 'Sold'),
    ]

    CONDITION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ]

    DURATION_CHOICES = [
        ('3', '3 Days'),
        ('7', '7 Days'),
        ('30', '30 Days'),
    ]

    title = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=200, null=True, blank=True)

    brand = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, choices=CATEGORIES)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(null=True, blank=True, db_index=True) 

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
            self.slug = f'{base_slug}'

            # Check if the slug is unique and adjust if necessary
            existing_slugs = Listing.objects.filter(slug__startswith=self.slug).count()
            if existing_slugs:
                self.slug = f'{self.slug}-{existing_slugs + 1}'

            # Calculate close date based on duration
            if self.duration and not self.close_date:
                days = int(self.duration)
                self.close_date = datetime.now() + timedelta(days=days)

        super(Listing, self).save(*args, **kwargs)

    def __str__(self):
        return f'Listing ID: {self.slug} with price {self.starting_price} is status {self.status} and closes at {self.close_date}'


class ListingImage(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='listing_images')
    image = models.ImageField(upload_to='listing_images/')  # Update this line

    def __str__(self):
        return f'Image for Listing ID: {self.listing.id}'

    def get_upload_path(instance, filename):
        """
        Function to determine the upload path dynamically.
        Saves files to: auctions/customer_email/listing_id/filename
        """
        listing_id = instance.listing.id
        return os.path.join('auctions', str(listing_id), filename)

    image = models.ImageField(upload_to=get_upload_path)

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
        ('Waiting Payment/Delivery', 'Waiting Payment/Delivery'),
        ('Payment Confirmed', 'Payment Confirmed'),
        ('Delivery Confirmed', 'Delivery Confirmed'),
        ('Transaction completed', 'Transaction Completed'),
        ('Transaction on Dispute', 'Transaction on Dispute'),
    ]
    serial_number = models.CharField(max_length=200, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Waiting Payment/Delivery')
    buyer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='buyer')
    seller = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='seller')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='product')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    # Closing
    delivered = models.BooleanField(default=False, blank=True, null=True)
    paid = models.BooleanField(default=False, blank=True, null=True)
    
    def __str__(self):
        return f'Transaction ID: {self.serial_number} with seller: {self.seller.email} and buyer: {self.buyer.email} with status: {self.status} for {self.amount}'
    

class Dispute(models.Model):
    STATUS_CHOICES = [
        ('Dispute Initiated', 'Dispute Initiated'),
        ('Dispute in Analysis', 'Dispute in Analysis'),
        ('Resolved for Buyer', 'Resolved for Buyer'),
        ('Resolved for Seller', 'Resolved for Seller')
    ]
    transaction_number = models.CharField(max_length=200, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Dispute Initiated')
    buyer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='buyer_disputed')
    seller = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='seller_disputed')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='product_disputed')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return f'Dispute for: {self.transaction_number} with seller: {self.seller.email} and buyer: {self.buyer.email} with status: {self.status}'








