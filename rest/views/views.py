

from ..models import *

from .viewslistings import *

from .viewscustomers import *

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest

# views for customers
def get_customer(request, identifier):
    print(identifier)
    response = retrieve_customer(request, identifier)
    return response

def phone_customer(request, phone):
    django_request = HttpRequest()
    django_request.method = request.method
    django_request.GET = request.GET
    django_request.POST = request.POST
    django_request.user = request.user
    
    response = retrieve_customer(django_request, phone)
    return response

@csrf_exempt
# views for listings
def new_listing(request):
    response = create_listing(request)
    return response

@csrf_exempt
# views for listings
def updatelisting(request):
    response = update_listing(request)
    return response

def get_mylistings(request, identifier):
    response = my_listings(request, identifier)
    return response

