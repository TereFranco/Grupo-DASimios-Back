from rest_framework import serializers
from django.utils import timezone
from .models import Category, Auction, Bid, Rating, Comment
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import NotFound, ValidationError
from datetime import timedelta
from django.db.models import Avg


class CategoryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AuctionListCreateSerializer(serializers.ModelSerializer):
    auctioneer_name = serializers.SerializerMethodField()
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
    # rating = serializers.DecimalField(
    #     max_digits=3, decimal_places=2,
    #     error_messages={"required": "La valoración es obligatoria."}
    # )
    stock = serializers.IntegerField(error_messages={"required": "El stock es obligatorio.",})
    brand = serializers.CharField(error_messages={"required": "La marca es obligatoria.",})
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages={"required": "La categoría es obligatoria."}
    )
    thumbnail = serializers.ImageField(required=True)
    isOpen = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)
    media_rating = serializers.SerializerMethodField(read_only=True) 

    class Meta:
        model = Auction
        fields = [
        'id', 'title', 'description', 'price', 'stock',
        'brand', 'category', 'category_name', 'thumbnail',
        'creation_date', 'closing_date', 'isOpen', 'auctioneer_name', 'media_rating'
    ]

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price has to be positive and higher than zero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Valoration has to be between 1 and 5")
        return value

    def get_media_rating(self, obj):
        avg = obj.ratings.aggregate(Avg("rating"))["rating__avg"]
        return round(avg or 1, 2)
    
    def validate(self, data):
        closing_date = data.get("closing_date")
        creation_time = timezone.now()  # Obtén la fecha y hora actuales, ya que creation_date es read_only

        # La fecha de cierre sea posterior a la fecha de creación (actual)
        if closing_date <= creation_time:
            raise serializers.ValidationError({
                "closing_date": "The closing date must be later than the current date."
            })

        # Verifica que la fecha de cierre sea al menos 15 días posterior a la fecha de creación
        if closing_date < creation_time + timedelta(days=15):
            raise serializers.ValidationError({
                "closing_date": "The closing date must be at least 15 days after the current date."
            })

        return data
    
    #para poder ver el nombre de la categoría
    def get_category_name(self, obj):
        return obj.category.name
    
    def get_auctioneer_name(self, obj):
        return f"{obj.auctioneer.first_name} {obj.auctioneer.last_name}" if obj.auctioneer else "Anónimo"

class AuctionDetailSerializer(serializers.ModelSerializer):
    auctioneer_name = serializers.SerializerMethodField()
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ",
    read_only=True)
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")   
    isOpen = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = [
        'id', 'title', 'description', 'price', 'stock',
        'brand', 'category', 'category_name', 'thumbnail',
        'creation_date', 'closing_date', 'isOpen', 'auctioneer_name'
    ]


    @extend_schema_field(serializers.BooleanField()) 
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price has to be positive and higher than zero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Valoration has to be between 1 and 5")
        return value

    
    def validate(self, data):
        closing_date = data.get("closing_date")
        creation_time = timezone.now()  # Obtén la fecha y hora actuales, ya que creation_date es read_only

        # La fecha de cierre sea posterior a la fecha de creación (actual)
        if closing_date <= creation_time:
            raise serializers.ValidationError({
                "closing_date": "The closing date must be later than the current date."
            })

        # Verifica que la fecha de cierre sea al menos 15 días posterior a la fecha de creación
        if closing_date < creation_time + timedelta(days=15):
            raise serializers.ValidationError({
                "closing_date": "The closing date must be at least 15 days after the current date."
            })

        return data
    
    def get_category_name(self, obj):
        return obj.category.name
    
    def get_auctioneer_name(self, obj):
        return f"{obj.auctioneer.first_name} {obj.auctioneer.last_name}" if obj.auctioneer else "Anónimo"
    

class BidListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    bidder = serializers.StringRelatedField(read_only=True)
    auction = serializers.PrimaryKeyRelatedField(read_only=True)
    auction_title = serializers.SerializerMethodField()

    class Meta:
        model = Bid
        fields = ['id', 'auction', 'auction_title', 'price', 'creation_date', 'bidder']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser positivo.")
        return value

    def validate(self, data):
        request = self.context.get("request")
        auction = self.context.get("auction")

        if not auction:
            raise serializers.ValidationError("La subasta asociada no está definida.")

        price = data.get("price")

        highest_bid = auction.bids.order_by('-price').first()
        if highest_bid and price <= highest_bid.price:
            raise serializers.ValidationError("La puja debe ser mayor que la anterior.")
        if not highest_bid and price <= auction.price:
            raise serializers.ValidationError("La puja debe ser mayor que el precio inicial.")

        return data

    def get_auction_title(self, obj):
        return obj.auction.title



class BidDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", 
    read_only=True) 
    auction_title = serializers.SerializerMethodField()

    class Meta: 
        model = Bid 
        #fields = '__all__' 
        fields = ['id', 'price', 'creation_date', 'auction', 'auction_title']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser positivo.")
        return value
    
    def validate(self, data):
        #auction = data.get('auction')
        auction = data.get('auction', getattr(self.instance, 'auction', None))
        price = data.get('price')

        if auction.closing_date < timezone.now():
            raise serializers.ValidationError("Auction is closed.")

        highest_bid = auction.bids.order_by('-price').first()
        if highest_bid and price <= highest_bid.price:
            raise serializers.ValidationError("The bid must be higher than the previous one.")
        if not highest_bid and price <= auction.starting_price:
            raise serializers.ValidationError("The bid must be higher than the starting price.")
        return data
    
    def get_auction_title(self, obj):
        return obj.auction.title
    

class UserBidSerializer(serializers.ModelSerializer):
    auction_title = serializers.SerializerMethodField()
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    bidder = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'auction', 'auction_title', 'price', 'creation_date', 'bidder']

    def get_auction_title(self, obj):
        return obj.auction.title if obj.auction else ""
    
    def validate(self, data):
        auction = data.get('auction')
        price = data.get('price')
        user = self.context['request'].user

        if auction.closing_date < timezone.now():
            raise serializers.ValidationError("Auction is closed.")

        highest_bid = auction.bids.order_by('-price').first()
        if highest_bid and price <= highest_bid.price:
            raise serializers.ValidationError("The bid must be higher than the previous one.")

        # Si el usuario ya tiene una puja, que solo pueda mejorarla
        existing_user_bid = auction.bids.filter(bidder=user).first()
        if existing_user_bid and price <= existing_user_bid.price:
            raise serializers.ValidationError("You must increase your previous bid.")

        return data
    

class RatingListCreateSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') 
    auction = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'rating', 'user', 'auction']

    def create(self, validated_data):
        user = self.context['request'].user
        auction = validated_data['auction']
        value = validated_data['rating']
        
        # actualizar si ya existe
        rating, created = Rating.objects.update_or_create(
            user=user,
            auction=auction,
            defaults={'rating': value}
        )
        return rating


class RatingUpdateRetrieveSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Rating
        fields = ['id', 'rating', 'user', 'auction']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    auction_title = serializers.ReadOnlyField(source='auction.title')

    class Meta:
        model = Comment
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'user', 'auction', 'auction_title']
