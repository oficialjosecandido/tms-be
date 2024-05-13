from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest.serializers import TransactionsSerializer
from rest.models import *

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