from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


from rest.models import *
import json
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def charge(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data['token']
        amount = data['amount']
        customer_id = data['customer_id']
        type = data['type']
        
        # Increase free deposit
        customer = Customer.objects.get(id=customer_id)
        customer.free_deposit = customer.free_deposit + amount
        customer.save()

        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # Stripe amount is in cents
                currency='eur',
                description='Payment description',
                source=token,
            )


            # Create the transaction after a successful charge
            stripe_movement = Stripe.objects.create(
                amount=amount,
                customer = customer,
                type = type,
                
            )

            return JsonResponse({'success': True, 'charge': charge, 'stripe_movement': stripe_movement.id}, status=200)
        except stripe.error.StripeError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)