# myapp/serializers.py
from rest_framework import serializers
from .models import *


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file']

class ListingSerializer(serializers.ModelSerializer):
    images = FileSerializer(many=True, required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=True)

    class Meta:
        model = Listing
        fields = '__all__'

class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
    
