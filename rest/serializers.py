# myapp/serializers.py
from rest_framework import serializers
from .models import CustomUser, Listing, Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class Productserializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['vendor'] = instance.vendor.username
        return representation
