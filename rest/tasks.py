# rest/tasks.py

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Listing

@shared_task
def close_expired_listings():
    # Get all listings with a close_date that has passed and status not yet 'Closed'
    expired_listings = Listing.objects.filter(close_date__lt=timezone.now()).exclude(status='Closed')

    for listing in expired_listings:
        # Update status to 'Closed'
        listing.status = 'Closed'
        listing.save()

        # Send an email notification to support@tms.com
        subject = f'Listing Closed: {listing.title}'
        message = f'The listing "{listing.title}" has been automatically closed as its close date has passed.'
        from_email = settings.EMAIL_HOST_USER
        to_email = ['josecandido@gmail.com']
        send_mail(subject, message, from_email, to_email)
