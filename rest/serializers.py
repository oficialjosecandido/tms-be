# myapp/serializers.py
from rest_framework import serializers
from .models import *


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = '__all__'

class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class BidSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()  # Custom field to handle customer serialization

    class Meta:
        model = Bid
        fields = ['id', 'created_at', 'bid', 'status', 'listing', 'customer']

    def get_customer(self, obj):
        # Assuming your Customer model has a 'verified' field
        if obj.customer.verified:  # If customer is verified
            return {
                "customer_id": obj.customer.id,
                "seller_id": obj.listing.customer.id,
                "verified": obj.customer.verified
            }
        else:  # If customer is not verified, return limited information
            return {
                "customer_id": obj.customer.id,
                "seller_id": obj.listing.customer.id,
                "verified": obj.customer.verified
            }


    
