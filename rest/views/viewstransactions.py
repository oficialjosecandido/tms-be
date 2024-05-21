from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


from rest.serializers import TransactionsSerializer
from rest.models import *
import json
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['GET, POST, DELETE'])
def get_transactions(request, listing_id):
    print(listing_id)
    try:
        transactions = Transaction.objects.filter(listing_id=listing_id)
        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'id': transaction.id,
                'status': transaction.status,
                'seller_name': transaction.seller_name,
                'seller_email': transaction.seller_email,
                'seller_phone_number': transaction.seller_phone_number,
                'buyer_name': transaction.buyer_name,
                'buyer_email': transaction.buyer_email,
                'buyer_phone_number': transaction.buyer_phone_number,
            })
        return Response(transaction_data)
    except Transaction.DoesNotExist:
        return Response({"error": "Transactions not found"}, status=404)

@api_view(['GET'])
def my_payments(request, identifier):
    try:
        transactions = Transaction.objects.filter(seller_email=identifier)
        serializer = TransactionsSerializer(transactions, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Transactions not found"}, status=404)
    
@api_view(['GET'])
def my_receivals(request, identifier):
    try:
        transactions = Transaction.objects.filter(buyer_email=identifier)
        serializer = TransactionsSerializer(transactions, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Transactions not found"}, status=404)
    


@api_view(['POST'])
def new_payment_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        status = data.get('status')
        seller_name = data.get('seller_name')
        seller_email = data.get('seller_email')
        seller_phone = data.get('seller_phone_number')
        buyer_name = data.get('buyer_name')
        buyer_email = data.get('buyer_email')
        buyer_phone = data.get('buyer_phone_number')
        items = data.get('items')

        Transaction.objects.create(
            amount=amount,
            status=status,
            seller_name=seller_name,
            seller_email=seller_email,
            seller_phone_number=seller_phone,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            buyer_phone_number=buyer_phone,
            items=items
        )

        # Increase seller balance
        customer = Customer.objects.get(email= seller_email)
        customer.balance = customer.balance + amount
        customer.save()


        # send mail to seller
        subject = 'Your Item was Sold'
        message = render_to_string('emails/success_sell.html', {
            'listing_id': items,
            'customer_name': seller_name,
            'dashboard_link': 'https://www.tms.com/dashboard/listing/' + str(items)
        })
        plain_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [seller_email]
        send_mail(subject, plain_message, from_email, to_email, html_message=message)

        return JsonResponse({'message': 'Payment created successfully'}, status=201)
        
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def charge(request):
    print(3333, request.body)
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data['token']
        amount = data['amount']

        # Extract additional fields for the Transaction model
        seller_name = data.get('seller_name', 'Seller')
        seller_email = data.get('seller_email', 'seller@example.com')
        seller_phone_number = data.get('seller_phone_number', '0000000000')
        buyer_name = data.get('buyer_name', 'Buyer')
        buyer_email = data.get('buyer_email', 'buyer@example.com')
        buyer_phone_number = data.get('buyer_phone_number', '0000000000')
        items = data.get('items', '')

        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # Stripe amount is in cents
                currency='usd',
                description='Payment description',
                source=token,
            )

            # Create the transaction after a successful charge
            transaction = Transaction.objects.create(
                amount=amount,
                status='Done',
                seller_name=seller_name,
                seller_email=seller_email,
                seller_phone_number=seller_phone_number,
                buyer_name=buyer_name,
                buyer_email=buyer_email,
                buyer_phone_number=buyer_phone_number,
                items=items,
            )

            return JsonResponse({'success': True, 'charge': charge, 'transaction_id': transaction.id}, status=200)
        except stripe.error.StripeError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
