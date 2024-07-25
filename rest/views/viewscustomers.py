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
import json


@api_view(['POST'])
def create_customer(request):
    print('Request data:', request.data)
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Regular Django view for filtering customers
@csrf_exempt
def filter_customer(request):
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        identifier = data.get('identifier')

        print('identifier:', identifier)

        if '@' in identifier:
            customer, created = Customer.objects.get_or_create(email=identifier)
        else:
            identifier = '+' + identifier
            customer, created = Customer.objects.get_or_create(phone_number=identifier)
            print(identifier, customer)

        print(customer)
        # Serialize the customer data
        serializer = CustomerSerializer(customer)
        # customer_data = {'id': customer.id, 'email': customer.email, 'phone_number': customer.phone_number}
        # Return the serialized data with appropriate status code
        return JsonResponse(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

    except Exception as e:
        # Handle any exceptions that might occur during the process
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def customer_detail(request, id):
    try:
        customer = Customer.objects.get(id=id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

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
def get_create_customer(request, id):
    identifier = '+' + str(id)
    print(identifier)
    
    # get_or_create returns a tuple: (instance, created)
    customer, created = Customer.objects.get_or_create(phone_number=identifier)
    
    # Pass the customer instance to the serializer
    serializer = CustomerSerializer(customer)
    
    return Response(serializer.data)


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
    
