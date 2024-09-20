import json
from rest.serializers import *
from rest_framework.decorators import api_view
from rest.models import *
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone


@api_view(['GET'])
def close_auctions(request):
    end_auctions = 0
    for listing in Listing.objects.all():
        if listing.close_date and listing.close_date < timezone.now():
                # Update the status to 'Closed' if the close_date has passed
                listing.status = 'Closed'
                end_auctions += 1
                listing.save()

    return Response({'Listings closed': end_auctions }, status=200)

@api_view(['GET'])
def hold_listing(request):
    # Get listings that are 'Closed' and 48 hours have passed since close_date
    threshold_time = timezone.now() - timedelta(hours=48)
    listings = Listing.objects.filter(status='Closed', close_date__lte=threshold_time)
    for listing in listings:
        # Update the status of the listing to 'On hold'
        listing.status = 'On hold'
        listing.save()


        # Send email notification to the user
        subject = 'Listing Moved on Hold '
        message = render_to_string('emails/listing_closed_actions.html', {
            'customer_name': listing.customer.display_name,
            'dashboard_link': 'https://trademyspin.web.app/listing/' + str(listing.slug)
        })
        plain_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [listing.customer.email]
        send_mail(subject, plain_message, from_email, to_email, html_message=message)
        
        

    return Response({'Listings updated to "On hold"': listings.count()}, status=200)

         

@api_view(['GET'])
def force_confirm_payment(request):
    pass


@api_view(['GET'])
def force_confirm_delivery(request):
    pass

@api_view(['GET'])
def force_dispute_statement(request):
    pass