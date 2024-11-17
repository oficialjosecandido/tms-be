

from ..models import *

from .viewslistings import *
from .viewscustomers import *
from .viewstransactions import *
from .stripeviews import *
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stripe_charge(request):
    response = charge(request)
    return response



