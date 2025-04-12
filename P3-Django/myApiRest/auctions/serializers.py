from rest_framework import serializers
from django.utils import timezone
from .models import Category, Auction, Bid
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import NotFound, ValidationError
from datetime import timedelta



class CategoryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# class AuctionListCreateSerializer(serializers.ModelSerializer):
#     creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ",
#     read_only=True)
#     closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
#     isOpen = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = Auction
#         fields = '__all__'

#     @extend_schema_field(serializers.BooleanField()) 
#     def get_isOpen(self, obj):
#         return obj.closing_date > timezone.now()

class AuctionListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )
    closing_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ",
        error_messages={
            "invalid": "Introduce una fecha válida.",
            "required": "La fecha de cierre es obligatoria."
        }
    )
    title = serializers.CharField(error_messages={"required": "El título es obligatorio."})
    description = serializers.CharField(error_messages={"required": "La descripción es obligatoria."})
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        error_messages={"required": "El precio es obligatorio."}
    )
    rating = serializers.DecimalField(
        max_digits=3, decimal_places=2,
        error_messages={"required": "La valoración es obligatoria."}
    )
    stock = serializers.IntegerField(error_messages={"required": "El stock es obligatorio."})
    brand = serializers.CharField(error_messages={"required": "La marca es obligatoria."})
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages={"required": "La categoría es obligatoria."}
    )
    thumbnail = serializers.URLField(
        error_messages={
            "required": "La URL de la imagen es obligatoria.",
            "invalid": "Introduce una URL válida."
        }
    )
    isOpen = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = [
        'id', 'title', 'description', 'price', 'rating', 'stock',
        'brand', 'category', 'category_name', 'thumbnail',
        'creation_date', 'closing_date', 'isOpen'
    ]

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser un número positivo.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("La valoración debe estar entre 1 y 5.")
        return value

    
    def validate(self, data):
        closing_date = data.get("closing_date")
        creation_time = timezone.now()  # Obtén la fecha y hora actuales, ya que creation_date es read_only

        # La fecha de cierre sea posterior a la fecha de creación (actual)
        if closing_date <= creation_time:
            raise serializers.ValidationError({
                "closing_date": "La fecha de cierre debe ser posterior a la fecha actual."
            })

        # Verifica que la fecha de cierre sea al menos 15 días posterior a la fecha de creación
        if closing_date < creation_time + timedelta(days=15):
            raise serializers.ValidationError({
                "closing_date": "La fecha de cierre debe ser al menos 15 días posterior a la fecha actual."
            })

        return data
    
    #para poder ver el nombre de la categoría
    def get_category_name(self, obj):
        return obj.category.name

class AuctionDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ",
    read_only=True)
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")   
    isOpen = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)
    #aquí se deberían ver las pujas?

    class Meta:
        model = Auction
        fields = '__all__' 

    @extend_schema_field(serializers.BooleanField()) 
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser un número positivo.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("La valoración debe estar entre 1 y 5.")
        return value

    
    def validate(self, data):
        closing_date = data.get("closing_date")
        creation_time = timezone.now()  # Obtén la fecha y hora actuales, ya que creation_date es read_only

        # La fecha de cierre sea posterior a la fecha de creación (actual)
        if closing_date <= creation_time:
            raise serializers.ValidationError({
                "closing_date": "La fecha de cierre debe ser posterior a la fecha actual."
            })

        # Verifica que la fecha de cierre sea al menos 15 días posterior a la fecha de creación
        if closing_date < creation_time + timedelta(days=15):
            raise serializers.ValidationError({
                "closing_date": "La fecha de cierre debe ser al menos 15 días posterior a la fecha actual."
            })

        return data
    
    def get_category_name(self, obj):
        return obj.category.name

    
class BidListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", 
    read_only=True) 

    class Meta: 
        model = Bid 
        fields = [
        'id', 'title', 'description', 'price', 'rating', 'stock',
        'brand', 'category', 'category_name', 'thumbnail',
        'creation_date', 'closing_date', 'auctioneer', 'isOpen'
    ]

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