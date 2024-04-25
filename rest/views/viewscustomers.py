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
def get_customer(request, email):
    try:
        customer = Customer.objects.get(email=email)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
