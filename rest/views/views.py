

from ..models import *

from .viewslistings import *

from .viewscustomers import *

from django.views.decorators.csrf import csrf_exempt

# views for customers
def get_customer(request, identifier):
    print(identifier)  # Print the identifier to verify it's received correctly
    # Dummy response for testing
    response = retrieve_customer(request, identifier)
    return response

@api_view(['GET'])
def phone_customer(request, phone):
    print(phone)
    # Dummy response for testing
    return JsonResponse({'message': 'Customer found'}, status=200)

@csrf_exempt
# views for listings
def new_listing(request):
    response = create_listing(request)
    return response


def get_mylistings(request, identifier):
    response = my_listings(request, identifier)
    return response

