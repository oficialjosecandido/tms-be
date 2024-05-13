from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework import status
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