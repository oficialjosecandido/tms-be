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
    
""" @api_view(['GET, POST, DELETE'])
def retrieve_customer(request, identifier):

    print(1111, identifier)
    try:
        # Check if the identifier is an email address
        if '@' in identifier:
            print('identifier is an email', identifier)
            customer, created = Customer.objects.get_or_create(email=identifier)
        # Check if the identifier is a phone number
        else:
            print('identifier is phone number', identifier)
            identifier.replace('identifier-', '+')
            # identifier = '+' + identifier
            # Try to get the customer by phone number
            print(identifier)
            customer, created = Customer.objects.get_or_create(phone_number=identifier)
            print('customer here....', customer)
        
        # Serialize the customer data
        serializer = CustomerSerializer(customer)
        # Return the serialized data with appropriate status code
        return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
    except Exception as e:
        # Handle any exceptions that might occur during the process
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) """