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
import random
import string

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
@api_view(['POST'])
def accept_offer(request):
    data = request.data
    amount = data.get('bid')
    status = 'Waiting Payment/Delivery'
    listing_id = data.get('listing')

    listing = Listing.objects.get(id=listing_id)
    seller = listing.customer
    buyer = Customer.objects.get(id=data.get('customer'))

    serial_number = generate_serial_number()

    # Calculate the frozen deposit for both buyer and seller (30% of transaction amount)
    frozen_deposit_buyer = freeze_deposit(amount)
    frozen_deposit_seller = freeze_deposit(amount)

    # Check if buyer and seller have enough free deposit
    if buyer.free_deposit < frozen_deposit_buyer:
        return JsonResponse({'error': 'Buyer does not have enough free deposit'}, status=400)

    if seller.free_deposit < frozen_deposit_seller:
        return JsonResponse({'error': 'Seller does not have enough free deposit'}, status=400)

    # Freeze 30% of the transaction amount for both buyer and seller
    buyer.frozen_deposit += frozen_deposit_buyer
    buyer.free_deposit -= frozen_deposit_buyer  # Deduct from buyer's free deposit
    buyer.save()

    seller.frozen_deposit += frozen_deposit_seller
    seller.free_deposit -= frozen_deposit_seller  # Deduct from seller's free deposit
    seller.save()

    transaction = Transaction.objects.create(
        amount=amount,
        status=status,
        buyer=buyer,
        seller=seller,
        listing=listing,
        serial_number=serial_number
    )

    listing.status = 'Waiting Payment/Delivery'
    listing.save()

    # Send notification emails to buyer and seller as in your original code...

    # Return the serialized transaction data
    return JsonResponse({'message': 'Transaction created successfully', 'transaction': {
            'transaction_id': transaction.serial_number,
            'buyer': {'name': buyer.display_name, 'email': buyer.email, 'phone': buyer.phone_number},
            'seller': {'name': seller.display_name, 'email': seller.email, 'phone': seller.phone_number},
            'status': transaction.status,
            'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }}, status=201)

@csrf_exempt
@api_view(['POST'])
def new_payment_order(request):
    data = request.data
    amount = data.get('amount')
    status = 'Waiting Payment/Delivery'
    listing_id = data.get('listing')
    seller_id = data.get('seller')
    buyer_email = data.get('buyer')

    listing = Listing.objects.get(id=listing_id)
    seller = Customer.objects.get(id=seller_id)
    buyer = Customer.objects.get(email=buyer_email)

    serial_number = generate_serial_number()

    # Calculate the frozen deposit for both buyer and seller (30% of transaction amount)
    frozen_deposit_buyer = freeze_deposit(amount)
    frozen_deposit_seller = freeze_deposit(amount)

    # Check if buyer and seller have enough free deposit
    if buyer.free_deposit < frozen_deposit_buyer:
        return JsonResponse({'error': 'Buyer does not have enough free deposit'}, status=400)

    if seller.free_deposit < frozen_deposit_seller:
        return JsonResponse({'error': 'Seller does not have enough free deposit'}, status=400)

    # Freeze 30% of the transaction amount for both buyer and seller
    buyer.frozen_deposit += frozen_deposit_buyer
    buyer.free_deposit -= frozen_deposit_buyer  # Deduct from buyer's free deposit
    buyer.save()

    seller.frozen_deposit += frozen_deposit_seller
    seller.free_deposit -= frozen_deposit_seller  # Deduct from seller's free deposit
    seller.save()

    transaction = Transaction.objects.create(
        amount=amount,
        status=status,
        buyer=buyer,
        seller=seller,
        listing=listing,
        serial_number=serial_number
    )

    # Send notification emails to buyer and seller as in your original code...

    # Return the serialized transaction data
    return JsonResponse({'message': 'Transaction created successfully', 'transaction': {
            'transaction_id': transaction.serial_number,
            'buyer': {'name': buyer.display_name, 'email': buyer.email, 'phone': buyer.phone_number},
            'seller': {'name': seller.display_name, 'email': seller.email, 'phone': seller.phone_number},
            'status': transaction.status,
            'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }}, status=201)



@api_view(['GET'])
def transaction(request, serial_number):
    try:
        transaction = Transaction.objects.get(serial_number=serial_number)
        

        serializer = TransactionsSerializer(transaction)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=404)
    

@api_view(['POST'])
def confirm_transaction(request):
    data = request.data
    print(data)

    transaction = Transaction.objects.get(serial_number=data.get('serial_number'))

    if data.get('persona') == 'buyer':
        transaction.paid = True

    elif data.get('persona')== 'seller':
        transaction.delivered = True

    else:
        print('error here')

    transaction.save()

    amount = data.get('amount')
    buyer = Customer.objects.get(email = data.get('buyer'))
    seller = Customer.objects.get(email=data.get('seller'))
    
    if transaction.paid and transaction.delivered == True:

        # Release frozen deposits to buyer and seller
        buyer_released = release_buyer_deposit(transaction.amount)
        seller_released, platform_profit = release_seller_deposit(transaction.amount)

        # Update buyer's deposit
        buyer.frozen_deposit -= buyer_released  # Reduce frozen deposit
        buyer.free_deposit += buyer_released  # Return released deposit to free deposit
        buyer.save()

        # Update seller's deposit
        seller.frozen_deposit -= seller_released  # Reduce frozen deposit
        seller.free_deposit += seller_released  # Return released deposit to free deposit
        seller.save()

        # Send notification email for platform profit
        subject = 'Platform Profit Notification'
        message = f'The platform has profited 10% of the transaction amount, which equals ${platform_profit}.'
        from_email = settings.EMAIL_HOST_USER
        to_email = ['tms.josecandido@gmail.com']
        send_mail(subject, message, from_email, to_email)

        transaction.status = 'Transaction completed'
        transaction.save()

        # send mail to seller
        subject = 'Transaction complete'
        message = render_to_string('emails/success_sell.html', {
            'serial_number': transaction.serial_number,
            'dashboard_link': 'https://www.tms.com/dashboard/transaction/' + transaction.serial_number
        })

        plain_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [buyer.email, seller.email, 'tms.josecandido@gmail.com']
        send_mail(subject, plain_message, from_email, to_email, html_message=message)

    return JsonResponse({'success': True}, status=200)


@csrf_exempt
@api_view(['POST'])
def dispute_transaction(request):
    data = request.data
    print(request.data)
    
    # Assuming 'transactionId' is actually the 'serial_number' or another unique string identifier
    try:
        my_transaction = Transaction.objects.get(serial_number=data['transactionId'])
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    
    try:
        buyer = Customer.objects.get(email=data['buyer'])
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Buyer not found'}, status=404)

    try:
        seller = Customer.objects.get(email=data['seller'])
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Seller not found'}, status=404)
    
    claim = data.get('message', '')
    persona = data.get('persona', '')

    # Assuming Dispute model requires these fields
    dispute = Dispute.objects.create(
        transaction=my_transaction,
        buyer=buyer,
        seller=seller,
        message=claim,
        persona=persona
    )
    my_transaction.status = 'Transaction on Dispute'
    my_transaction.save()
    print('Dispute created successfully', dispute)

    # send mail to seller
    subject = 'Transaction on Dispute'
    message = render_to_string('emails/success_sell.html', {
        'serial_number': my_transaction.serial_number,
        'dashboard_link': 'https://www.tms.com/dashboard/transaction/' + my_transaction.serial_number
    })

    plain_message = strip_tags(message)
    from_email = settings.EMAIL_HOST_USER
    to_email = [buyer.email, seller.email, 'tms.josecandido@gmail.com']
    send_mail(subject, plain_message, from_email, to_email, html_message=message)

    return JsonResponse({'success': True}, status=200)


@api_view(['GET'])
def my_purchases(request, email):
    
    try:
        me = Customer.objects.get(email=email)
        print(me)
        transactions = Transaction.objects.filter(buyer=me)
        print(transactions.count())
        serializer = TransactionsSerializer(transactions, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Transactions not found"}, status=404)
    
@api_view(['GET'])
def my_sales(request, email):
    
    try:
        me = Customer.objects.get(email=email)
        print(me)
        transactions = Transaction.objects.filter(seller=me)
        print(transactions.count())
        serializer = TransactionsSerializer(transactions, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Transactions not found"}, status=404)
    


def generate_serial_number(length=20):
    characters = string.ascii_uppercase + string.digits  
    return ''.join(random.choices(characters, k=length))


def freeze_deposit(amount):
    # Freeze 30% of the transaction amount
    frozen_deposit = amount * 0.30
    return frozen_deposit

def release_buyer_deposit(amount):
    # Release the frozen 30% to the buyer
    released_deposit = amount * 0.30
    return released_deposit

def release_seller_deposit(amount):
    # Release 20% to the seller and keep 10% as platform profit
    released_deposit = amount * 0.20
    platform_profit = amount * 0.10
    return released_deposit, platform_profit


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
    print(identifier)
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
    
