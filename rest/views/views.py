

from ..models import *

from .viewslistings import *
from .viewscustomers import *
from .viewstransactions import *

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django.http import HttpRequest

# views for customers
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def get_customer(request):
    if request.method == 'POST':
        return filter_customer(request)
    else:
        # Handle GET requests if needed
        pass


# views for listings
def listings(request):
    response = all_listings(request)
    return response

@csrf_exempt
def new_listing(request):
    response = create_listing(request)
    return response

@csrf_exempt
def updatelisting(request):
    response = update_listing(request)
    return response

def get_mylistings(request, identifier):
    response = my_listings(request, identifier)
    return response

def listing_details(request, id):
    response = listing_detail(request, id)
    return response

@csrf_exempt
def upload_images(request):
    response = my_images(request)
    return response



#views for transactions
@csrf_exempt
def new_payment(request):
    print(444, request)
    response = new_payment_order(request)
    return response

def get_mypayments(request, identifier):
    response = my_payments(request, identifier)
    return response

def get_myreceivals(request, identifier):
    response = my_receivals(request, identifier)
    return response


def listing_transactions(request, identifier):
    response = get_transactions(request, identifier)
    return response


@csrf_exempt
def stripe_charge(request):
    response = charge(request)
    return response
