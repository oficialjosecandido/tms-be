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
    print(request.body)
    if request.method == 'POST':
        try:
            # Decode the JSON data from the request body
            data = json.loads(request.body)
            
            # Extract relevant data from the JSON
            asking_price = data.get('askingPrice')
            buy_date = data.get('buyDate')
            buy_date = convert_buy_date_format(buy_date)

            bike_condition = data.get('bikeCondition')
            bike_condition = convert_bike_condition_format(bike_condition)

            bike_options = json.dumps({option['name']: option['isChecked'] for option in data.get('bikeOptions', [])})
            bike_accessories = json.dumps({accessory['name']: accessory['isChecked'] for accessory in data.get('bikeAccessories', [])})
            customer_data = {
                'display_name': data.get('name'),
                'shipping_address': data.get('address'),
                'email': data.get('email'),
                'phone_number': data.get('phoneNumber')
            }

            # Create a new Customer object or retrieve an existing one
            customer, created = Customer.objects.get_or_create(email=customer_data['email'], defaults=customer_data)

            # Create a new Listing object
            listing = Listing.objects.create(
                buy_date=buy_date,
                bike_condition=bike_condition,
                bike_options=bike_options,
                bike_accessories=bike_accessories,
                asking_price=asking_price,
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
