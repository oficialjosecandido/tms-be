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
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, renderer_classes


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
        my_purchases = Transaction.objects.filter(buyer=customer)
        count_purchases = my_purchases.count()

        # Calculate total purchases amount
        total_purchases = sum(purchase.amount for purchase in my_purchases)

        # total sales and total amount in sales
        my_sales = Transaction.objects.filter(seller=customer)
        count_sales = my_sales.count()

        # Calculate total sales amount
        total_sales = sum(sale.amount for sale in my_sales)

        # active offers
        my_offers = Bid.objects.filter(customer=customer)
        active_offers = my_offers.filter(status='Active').count()

        # active listings
        my_listings = Listing.objects.filter(customer=customer)
        active_listings = my_listings.filter(status='Active').count()

        # active disputes
        my_disputes_seller = Dispute.objects.filter(seller=customer)
        my_disputes_buyer = Dispute.objects.filter(buyer=customer)
        active_disputes_seller = my_disputes_seller.filter(status='Active').count()
        active_disputes_buyer = my_disputes_buyer.filter(status='Active').count()
        active_disputes = active_disputes_seller + active_disputes_buyer

        # Prepare the response data
        customer_data = {
            'status': customer.status,
            'frozen_deposit': customer.frozen_deposit,
            'free_deposit': customer.free_deposit,
            'active_listings': active_listings,
            'active_offers': active_offers,
            'count_purchases': count_purchases,
            'total_purchases': total_purchases,
            'count_sales': count_sales,
            'total_sales': total_sales,
            'active_disputes': active_disputes
        }
        
        return Response(customer_data)

    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)


@api_view(['GET'])
@renderer_classes([JSONRenderer])  # Explicitly use JSONRenderer
def get_customer_email(request, id):    
    customer, created = Customer.objects.get_or_create(email=id)
    serializer = CustomerSerializer(customer)
    return Response(serializer.data)


@api_view(['GET'])
def get_customer_id(request, id):    
    # get_or_create returns a tuple: (instance, created)
    customer = Customer.objects.get(id=id)
    
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
            'free_deposit': customer.free_deposit
        })
        plain_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [customer.email]
        send_mail(subject, plain_message, from_email, to_email, html_message=message)

        # send mail to customer
        subject = 'Withdraw Funds Request'
        message = render_to_string('emails/request_withdraw.html', {
            'customer_name': customer.email,
            'free_deposit': customer.free_deposit
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
    
