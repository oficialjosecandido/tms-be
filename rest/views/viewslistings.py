import json
from rest_framework.decorators import api_view
from rest.models import Listing, Customer
from django.http import JsonResponse


@api_view(['POST'])
def create_listing(request):
    print(request.body)
    if request.method == 'POST':
        try:
            # Decode the JSON data from the request body
            data = json.loads(request.body)
            
            # Extract relevant data from the JSON
            buy_date = data.get('buyDate')
            bike_condition = data.get('bikeCondition')
            bike_options = {option['name']: option['isChecked'] for option in data.get('bikeOptions', [])}
            bike_accessories = {accessory['name']: accessory['isChecked'] for accessory in data.get('bikeAccessories', [])}
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
                customer=customer,
            )


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
