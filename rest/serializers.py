# myapp/serializers.py
from rest_framework import serializers
from .models import *
import datetime
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





def check_expiry_month(value):
    if not 1 <= int(value) <= 12:
        raise serializers.ValidationError("Invalid expiry month.")


def check_expiry_year(value):
    today = datetime.datetime.now()
    if not int(value) >= today.year:
        raise serializers.ValidationError("Invalid expiry year.")


def check_cvc(value):
    if not 3 <= len(value) <= 4:
        raise serializers.ValidationError("Invalid cvc number.")


def check_payment_method(value):
    payment_method = value.lower()
    if payment_method not in ["card"]:
        raise serializers.ValidationError("Invalid payment_method.")

class CardInformationSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=150, required=True)
    expiry_month = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_month],
    )
    expiry_year = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_year],
    )
    cvc = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_cvc],
    )