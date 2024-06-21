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

from rest_framework import viewsets


@api_view(['GET'])
def all_listings(request):
    try:
        listings = Listing.objects.order_by('-created_at')
        serializer = ListingSerializer(listings, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listings not found"}, status=404)

@api_view(['GET'])
def my_listings(request, identifier):

    print(2222, identifier)
    customer = Customer.objects.get(email=identifier)

    try:
        listings = Listing.objects.filter(customer=customer).order_by('-created_at')
        for listing in listings:
            if listing.status == 'Pending Confirmation':
                listing.status = 'Approved'
                print(listing)
                listing.save()
        serializer = ListingSerializer(listings, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listings not found"}, status=404)
    
@csrf_exempt  
@api_view(['POST'])
def create_listing(request):
    if request.method == 'POST':
        try:
            # Decode the JSON data from the request body
            data = json.loads(request.body)
            print(data)
            
            # Extract bike Info
            bike_data = data.get('bikeInfo')
            model = bike_data.get('pelotonModel')
            asking_price = bike_data.get('askingPrice')
            buy_date = bike_data.get('buyDate')
            buy_date = convert_buy_date_format(buy_date)



            bike_condition = bike_data.get('bikeCondition')
            bike_condition = convert_bike_condition_format(bike_condition)

            bike_options = {option['name']: option['isChecked'] for option in bike_data.get('bikeOptions', [])}
            bike_options_json = json.dumps(bike_options)
            bike_accessories = json.dumps({accessory['name']: accessory['isChecked'] for accessory in bike_data.get('bikeAccessories', [])})

            serial_number = bike_data.get('serialNumber')
            other_accessories = bike_data.get('otherCondition')
            other_condition = bike_data.get('otherAccessories')

            # Check if "Bike does not turn on" option is true
            if bike_options.get('Bike does not turn on', False):
                status = 'Rejected'
            else:
                status = 'Pending Confirmation'

            # Extract customer info
            customer_info = data.get('customerInfo')
            customer_data = {
                'display_name': customer_info.get('name'),
                'shipping_address': customer_info.get('address'),
                'email': customer_info.get('email'),
                'phone_number': customer_info.get('phoneNumber')
            }

            print(customer_data)

            # Check if a customer with the same email and phone number exists
            customer = Customer.objects.filter(email=customer_data['email'], phone_number=customer_data['phone_number']).first()

            # If a customer exists, use the existing customer
            if customer:
                created = False
            else:
                # Otherwise, create a new customer
                customer, created = Customer.objects.get_or_create(email=customer_data['email'], phone_number=customer_data['phone_number'], defaults=customer_data)

            # Create a new Listing object
            listing = Listing.objects.create(
                model=model,
                buy_date=buy_date,
                bike_condition=bike_condition,
                bike_options=bike_options_json,
                bike_accessories=bike_accessories,
                asking_price=asking_price,
                status=status,
                customer=customer,
                serial_number = serial_number,
                other_accessories = other_accessories,
                other_condition = other_condition
            )

            # Send email notification to the user
            subject = 'Listing Created and Pending Approval'
            message = render_to_string('emails/create_listing_success.html', {
                'listing_id': listing.id,
                'customer_name': customer.display_name,
                'dashboard_link': 'https://trademyspin.web.app/listing/' + str(listing.id)
            })
            plain_message = strip_tags(message)
            from_email = settings.EMAIL_HOST_USER
            to_email = [customer.email]
            send_mail(subject, plain_message, from_email, to_email, html_message=message)

            # Return a JSON response including the created listing
            return JsonResponse({'message': 'Listing created successfully', 'listing': {
                'id': listing.id,
                'customer': {
                    'name': customer.display_name,
                    'address': customer.shipping_address,
                    'email': customer.email,
                    'phone_number': customer.phone_number
                },
                'status': listing.status,
                'created_at': listing.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }}, status=201)
        except Exception as e:
            # Return an error response if something goes wrong
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # Return a method not allowed response for non-POST requests
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['POST'])
def my_images(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')
        listing_id = request.POST.get('listing_id')  # Get the listing ID from the request
        try:
            listing = Listing.objects.get(id=listing_id)
            listing.save_images(images)
            return JsonResponse({'message': 'Images uploaded successfully'}, status=201)
        except Listing.DoesNotExist:
            return JsonResponse({'error': 'Listing not found'}, status=404)
    else:
        return JsonResponse({'error': 'No images provided'}, status=400)

@api_view(['GET'])
def listing_detail(request, id):
    try:
        listing = Listing.objects.get(id=id)
        serializer = ListingSerializer(listing)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listing not found"}, status=404)

@csrf_exempt    
@api_view(['POST'])
def update_listing_status(request, id):
    
    listing = Listing.objects.get(id=id)
    if listing:
        listing.status = 'Pending Pickup'
        listing.save()
        return JsonResponse({'message': 'Listing updated successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Listing not found'}, status=404)


@csrf_exempt
@api_view(['POST'])
def create_comment(request):
    print(2222, request)
    if request.method == 'POST':
        try:
            # Decode the JSON data from the request body
            data = json.loads(request.body)
            print(data)
            
            # Extract comment details
            listing_id = data.get('listing')
            name = data.get('name')
            comment_text = data.get('comment')

            if not listing_id or not name or not comment_text:
                return JsonResponse({'error': 'Invalid input'}, status=400)

            # Get the listing object
            listing = Listing.objects.get(id=listing_id)

            # Create a new Comment object
            new_comment = Comment.objects.create(
                listing=listing,
                name=name,
                comment=comment_text
            )

            # Send email notification to the user
            subject = 'New Comment'
            message = render_to_string('emails/create_listing_success.html', {
                'listing_id': listing.id,
                'seller_name': listing.customer.display_name,  # Assuming the customer is the seller
                'dashboard_link': 'https://www.tms.com/seller/listing/' + str(listing.id)
            })
            plain_message = strip_tags(message)
            from_email = settings.EMAIL_HOST_USER
            to_email = [listing.customer.email]
            send_mail(subject, plain_message, from_email, to_email, html_message=message)

            # Return a JSON response including the created comment
            return JsonResponse({'message': 'Comment created successfully', 'comment': {
                'id': new_comment.id,
                'listing': new_comment.listing.id,
                'name': new_comment.name,
                'comment': new_comment.comment,
                'created_at': new_comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
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
def get_comments(request, id):


    try:
        comments = Comment.objects.filter(listing=id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Comments not found"}, status=404)


def convert_buy_date_format(buy_date):
    # Convert the buy date to appropriate format
    if buy_date == 'Before 2018':
        return 'Before 2018'
    elif buy_date == '2018 - 2020':
        return '2018 - 2020'
    elif buy_date == '2021 - 2022':
        return '2021 - 2022'
    elif buy_date == '2023 to present':
        return '2023 to present'
    else:
        return buy_date
    

def convert_bike_condition_format(bike_condition):
    # Convert the bike condition to appropriate format
    if bike_condition == 'Needs some love':
        return 'Needs some love'
    elif bike_condition == 'Works well (201-500 Rides)':
        return 'Works well (201-500 Rides)'
    elif bike_condition == 'Very good (51-200 Rides)':
        return 'Very good (51-200 Rides)'
    elif bike_condition == 'Excellent (0 - 50 Rides)':
        return 'Excellent (0 - 50 Rides)'
    else:
        return bike_condition


