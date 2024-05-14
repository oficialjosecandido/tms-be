import json
from rest.serializers import ListingSerializer
from rest_framework.decorators import api_view
from rest.models import Listing, Customer
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework.response import Response
from django.utils import timezone

@api_view(['GET'])
def all_listings(request):
    try:
        listings = Listing.objects.all()
        serializer = ListingSerializer(listings, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listings not found"}, status=404)

@api_view(['GET'])
def my_listings(request, identifier):

    print(2222, identifier)
    customer = Customer.objects.get(email=identifier)

    try:
        listings = Listing.objects.filter(customer=customer)
        serializer = ListingSerializer(listings, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listings not found"}, status=404)
    

@api_view(['POST'])
def create_listing(request):
    # print(request.body)
    if request.method == 'POST':
        try:
            # Decode the JSON data from the request body
            data = json.loads(request.body)
            print(data)
            
            # Extract bike Info
            bike_data = data.get('bikeInfo')
            model = bike_data.get('model')
            asking_price = bike_data.get('askingPrice')
            buy_date = bike_data.get('buyDate')
            buy_date = convert_buy_date_format(buy_date)

            bike_condition = bike_data.get('bikeCondition')
            bike_condition = convert_bike_condition_format(bike_condition)

            bike_options = json.dumps({option['name']: option['isChecked'] for option in bike_data.get('bikeOptions', [])})
            bike_accessories = json.dumps({accessory['name']: accessory['isChecked'] for accessory in bike_data.get('bikeAccessories', [])})

            # Check if "Cracked or Broken Screen" option is true
            # cracked_or_broken_screen = bike_data.get('bikeOptions', {}).get('Craked or Broken Screen', False)

            # Set the status based on the condition
            """ if cracked_or_broken_screen:
                status = 'Rejected'
            else:
                status = 'Approved' """

            status = 'Approved'

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
                bike_options=bike_options,
                bike_accessories=bike_accessories,
                asking_price=asking_price,
                status=status,
                customer=customer,
            )

            # Send email notification to the user
            subject = 'Listing Created and Pending Approval'
            message = render_to_string('emails/create_listing_success.html', {
                'listing_id': listing.id,
                'customer_name': data.get('name'),
                'dashboard_link': 'https://www.tms.com/dashboard/listing/' + str(listing.id)
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



@api_view(['POST'])
def update_listing(request):
    # Parse the byte object into a dictionary
    data = json.loads(request.body)

    # Get the original listing
    listing_id = data.get('id')
    listing = Listing.objects.filter(id=listing_id).first()
    if listing:
        # Update the asking price
        listing.asking_price = data.get('asking_price')
        listing.status = data.get('status')
        # listing = data
        listing.save()
        return JsonResponse({'message': 'Listing updated successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Listing not found'}, status=404)


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


