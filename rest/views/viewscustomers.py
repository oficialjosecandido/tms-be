from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from rest.serializers import CustomerSerializer
from ..models import Customer

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

@api_view(['GET'])
def retrieve_customer(request, identifier):
    print(2222, identifier)
    try:
        # Check if the identifier is an email address
        if '@' in identifier:
            customer = Customer.objects.get(email=identifier)
        # Check if the identifier is a phone number
        elif identifier.isdigit():
            # Assuming you have a field named "phone_number" in your Customer model
            identifier = '+' + identifier
            customer = Customer.objects.get(phone_number=identifier)
        else:
            # Handle invalid identifier format
            return Response({"error": "Invalid identifier format"}, status=400)
        
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
