from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from .models import *

def mark_listings_as_rejected():
    """
    Function to mark listings as rejected 30 days after they were created.
    """
    # Calculate the cutoff date (30 days ago)
    cutoff_date = timezone.now() - timezone.timedelta(days=30)
    
    # Get listings that are still in the "Active" status and were created more than 30 days ago
    expired_listings = Listing.objects.filter(status='Active', created_at__lte=cutoff_date)
    
    # Update the status of expired listings to "Rejected"
    for listing in expired_listings:
        listing.status = 'Rejected'
        listing.save()


def send_listing_reminder_emails():
    # Get listings created more than 2 days ago and still in "Active" status
    two_days_ago = timezone.now() - timedelta(days=2)
    listings = Listing.objects.filter(created_at__lte=two_days_ago, status='Active')

    for listing in listings:
        # Send email notification to the user
        subject = 'Listing Created and Pending Approval'
        message = render_to_string('emails/2days_reminder.html', {
            'listing_id': listing.id,
            'customer_name': listing.customer.display_name,
            'dashboard_link': 'https://www.tms.com/seller/listings/'
        })
        plain_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [listing.customer.email]
        send_mail(subject, plain_message, from_email, to_email, html_message=message)