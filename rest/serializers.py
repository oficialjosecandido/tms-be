# myapp/serializers.py
from rest_framework import serializers
from .models import *


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
        fields = ['id', 'model', 'buy_date', 'bike_condition', 'bike_options', 'bike_accessories', 'customer', 'asking_price', 'status', 'created_at', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Manually handle bike_options serialization
        if 'instance' in kwargs:
            # Check if instance is provided
            instance = kwargs['instance']
            if instance:
                # Convert bike_options JSON string to Python dictionary
                self.fields['bike_options'] = serializers.JSONField(source='get_bike_options_display', read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation
    

class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
    
