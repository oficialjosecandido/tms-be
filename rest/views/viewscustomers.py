from email.message import EmailMessage
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest.serializers import *
from ..models import *
from django.http import JsonResponse

@api_view(['PUT'])
def update_customer(request, id):
    try:
        customer = Customer.objects.get(id=id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    # Exclude image field if it's not being updated
    request_data = request.data.copy()
    request_data.pop('image', None)

    serializer = CustomerSerializer(customer, data=request_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def customer_info(request, email):
    try:
        customer = Customer.objects.get(email=email)
        
        # total purchases and total amount in purchases
        my_purchases = Transaction.objects.filter(buyer_email=customer.email)
        count_purchases = my_purchases.count()

        total_purchases = 0
        for purchase in my_purchases:
            total_purchases = total_purchases + purchase.amount
            total_purchases.save()


        # total sales and total amount in sales
        my_sales = Transaction.objects.filter(seller_email=customer.email)
        count_sales = my_sales.count()

        total_sales = 0
        for sale in my_sales:
            total_sales = total_sales + sale.amount
            total_sales.save()

        # active offers
        my_offers = Bid.objects.filter(customer=customer)
        active_offers = my_offers.filter(status='Active').count()

        # active listings
        my_listings = Listing.objects.filter(customer=customer)
        active_listings = my_listings.filter(status = 'Approved').count()

        # ratings
        # disputes

        # pending funds
        # free funds

        customer_data = {
                'status': customer.status,
                'balance': customer.balance,
                'active_listings': active_listings,
                'active_offers': active_offers,
                'count_purchases': count_purchases,
                'total_purchases': total_purchases,
                'count_sales': count_purchases,
                'total_sales': total_purchases
            }
        
        return Response(customer_data)
    except Listing.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)


@api_view(['GET'])
def get_customer_email(request, id):    
    # get_or_create returns a tuple: (instance, created)
    customer, created = Customer.objects.get_or_create(email=id)
    
    # Pass the customer instance to the serializer
    serializer = CustomerSerializer(customer)
    return Response(serializer.data)


@api_view(['POST'])
def request_withdraw(request):
    customer_id = request.data.get('customerId')
    try:
        customer = Customer.objects.get(id=customer_id)

        # send mail to customer
        subject = 'Withdraw Funds Request'
        message = render_to_string('emails/request_withdraw.html', {
            'customer_name': customer.display_name,
            'balance': customer.balance
        })
        plain_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [customer.email]
        send_mail(subject, plain_message, from_email, to_email, html_message=message)

        # send mail to customer
        subject = 'Withdraw Funds Request'
        message = render_to_string('emails/request_withdraw.html', {
            'customer_name': customer.email,
            'balance': customer.balance
        })
        plain_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [customer.email]
        send_mail(subject, plain_message, from_email, to_email, html_message=message)

        
        return Response({"message": "Withdrawal request sent successfully."})
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found."}, status=404)
    
@api_view(['POST'])
def upload_id(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')
        customer_email = request.POST.get('email')
        try:
            customer = Customer.objects.get(email=customer_email)
            customer.save_images(images)
            return JsonResponse({'message': 'Images uploaded successfully'}, status=201)
        except Listing.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)
    else:
        return JsonResponse({'error': 'No images provided'}, status=400)
    

@api_view(['POST'])
def upload_topup(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')
        customer_email = request.POST.get('email')

        # Send email notification to the user
        subject = 'Listing Created and Pending Approval'
        message = render_to_string('emails/proof_payment.html', {
            'customer': customer_email,
        })
        plain_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [customer_email, 'josevcandido@gmail.com']
        
        # Create the email
        email = EmailMessage(
            subject,
            plain_message,
            from_email,
            to_email,
        )
        email.content_subtype = 'html'

        # Attach images to the email
        for image in images:
            email.attach(image.name, image.read(), image.content_type)

        # Send the email
        email.send()

        return JsonResponse({'message': 'Proof of payment sent successfully'}, status=201)
        
    else:
        return JsonResponse({'error': 'No images provided'}, status=400)
    
