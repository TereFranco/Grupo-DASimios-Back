from rest_framework import serializers
from django.utils import timezone
from .models import Category, Auction, Bid
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import NotFound, ValidationError



class CategoryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class AuctionListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ",
    read_only=True)
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = '__all__'

    @extend_schema_field(serializers.BooleanField()) 
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()

class AuctionDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ",
    read_only=True)
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")   
    isOpen = serializers.SerializerMethodField(read_only=True)
    #aquí se deberían ver las pujas?

    class Meta:
        model = Auction
        fields = '__all__'

    @extend_schema_field(serializers.BooleanField()) 
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()
    
class BidListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", 
    read_only=True) 

    class Meta: 
        model = Bid 
        fields = '__all__' 

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser positivo.")
        return value
    
    def validate(self, data):
        auction = data.get('auction')
        price = data.get('price')

        if auction.closing_date < timezone.now():
            raise serializers.ValidationError("La subasta está cerrada.")

        highest_bid = auction.bids.order_by('-price').first()
        if highest_bid and price <= highest_bid.price:
            raise serializers.ValidationError("La puja debe ser mayor que la anterior.")
        if not highest_bid and price <= auction.starting_price:
            raise serializers.ValidationError("La puja debe ser mayor que el precio inicial.")
        return data

    
class BidDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", 
    read_only=True) 

    class Meta: 
        model = Bid 
        fields = '__all__' 

    #le permitimos modificar las pujas?
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser positivo.")
        return value
    
    def validate(self, data):
        auction = data.get('auction')
        price = data.get('price')

        if auction.closing_date < timezone.now():
            raise serializers.ValidationError("La subasta está cerrada.")

        highest_bid = auction.bids.order_by('-price').first()
        if highest_bid and price <= highest_bid.price:
            raise serializers.ValidationError("La puja debe ser mayor que la anterior.")
        if not highest_bid and price <= auction.starting_price:
            raise serializers.ValidationError("La puja debe ser mayor que el precio inicial.")
        return data