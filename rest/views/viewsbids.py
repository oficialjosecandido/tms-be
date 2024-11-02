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
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from rest_framework import viewsets


@csrf_exempt
@api_view(['POST'])
def post_bid(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            listing_id = data.get('listing')
            email = data.get('customer')
            bid = data.get('bid')
            listing = Listing.objects.get(slug=listing_id)
            # Create or get the customer instance
            customer, created = Customer.objects.get_or_create(email=email)

            new_bid = Bid.objects.create(
                listing=listing,
                customer=customer,
                bid=bid
            )
            # Log the customer and new bid for debugging
            print(f'Customer: {customer}, Created: {created}')
            print(f'New Bid: {new_bid}')

            # Send email notification to the user
            subject = 'Thanks for your bid'
            message = render_to_string('emails/N0004_thanks_bid.html', {
                'listing_title': listing.title,
                'customer_name': listing.customer.display_name,  # Assuming the customer is the seller
                'listing_link': 'https://www.tms.com/seller/listing/' + str(listing.id)
            })
            plain_message = strip_tags(message)
            from_email = settings.EMAIL_HOST_USER
            to_email = [listing.customer.email]
            send_mail(subject, plain_message, from_email, to_email, html_message=message)

            # Return a JSON response including the created comment
            return JsonResponse({'message': 'Offer created successfully', 'offer': {
                'id': new_bid.id,
                'listing': new_bid.listing.id,
                'name': new_bid.customer.display_name,
                'bid': new_bid.bid,
                'created_at': new_bid.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }}, status=201)
        except Listing.DoesNotExist:
            return JsonResponse({'error': 'Listing not found'}, status=404)
        except Exception as e:
            # Return an error response if something goes wrong
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # Return a method not allowed response for non-POST requests
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

@api_view(['GET'])
def get_bids(request, slug):
    print(slug)
    try:
        # Get the listing object based on the slug
        listing = Listing.objects.get(slug=slug)        
        # Get all bids associated with the listing
        bids = Bid.objects.filter(listing=listing).order_by('-created_at')
        # If no bids are found, return an empty list
        if not bids.exists():
            return Response([], status=status.HTTP_200_OK)
                
        # Serialize the queryset of bids
        serializer = BidSerializer(bids, many=True)  # Use many=True because filter() returns a queryset
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Listing.DoesNotExist:
        return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def get_my_bids(request, email):
    try:
        bidder = Customer.objects.get(email=email)
        # Get all bids associated with the listing
        bids = Bid.objects.filter(customer=bidder)
        
        # If no bids are found, return an empty list
        if not bids.exists():
            return Response([], status=status.HTTP_200_OK)
        
        print(222222, bids)
        
        # Serialize the queryset of bids
        serializer = BidSerializer(bids, many=True)  # Use many=True because filter() returns a queryset
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Listing.DoesNotExist:
        return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)