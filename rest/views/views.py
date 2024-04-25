

from ..models import *

from .viewslistings import *

from .viewscustomers import *

from django.views.decorators.csrf import csrf_exempt


# views for customers
def get_customer(request):
    response = get_customer(request)
    return response

@csrf_exempt
# views for listings
def new_listing(request):
    response = create_listing(request)
    return response
