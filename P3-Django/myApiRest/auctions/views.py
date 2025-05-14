from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Category, Auction, Bid, Rating, Comment, WalletTransaction
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidDetailSerializer, BidListCreateSerializer, UserBidSerializer, RatingListCreateSerializer, RatingUpdateRetrieveSerializer, CommentSerializer, WalletTransactionSerializer
from decimal import Decimal
from django.db.models import Q
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated 
from rest_framework.response import Response 
from .permissions import IsOwnerOrAdmin 
from django.utils import timezone
from django.db.models import Avg
 
# Create your views here.
class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer
 
 
class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]  
    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer

    # Si no existe una subasta introducida en la url
    def get_object(self):
        try:
            auction = Auction.objects.get(pk=self.kwargs['pk'])
        except Auction.DoesNotExist:
            raise NotFound(detail="La subasta solicitada no existe.")
        return auction

class BidListCreate(generics.ListCreateAPIView):
    serializer_class = BidListCreateSerializer

    def get_queryset(self):
        return Bid.objects.filter(auction_id=self.kwargs['auction_id'])

    def perform_create(self, serializer):
        auction = Auction.objects.get(id=self.kwargs['auction_id'])
        user = self.request.user
        price = serializer.validated_data['price']

        saldo = sum([
            t.amount if t.is_deposit else -t.amount
            for t in user.wallet_transactions.all()
        ])

        if saldo < price:
            raise ValidationError("Saldo insuficiente para realizar la puja.")

        serializer.save(auction=auction, bidder=user)

        WalletTransaction.objects.create(
            user=user,
            card_number="PUJA",
            amount=price,
            is_deposit=False
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['auction'] = Auction.objects.get(id=self.kwargs['auction_id'])
        return context
 
class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidDetailSerializer
   
    def get_queryset(self): #sobreescribimos este método para devovler lo que queremos
        return Bid.objects.filter(auction_id=self.kwargs['auction_id'])
   
 
class AuctionListCreate(generics.ListCreateAPIView):
    serializer_class = AuctionListCreateSerializer
 
    def get_queryset(self):
        queryset = Auction.objects.all()
        texto = self.request.query_params.get('search')
        categoria = self.request.query_params.get('category_id')
        precio_min = self.request.query_params.get('min_price')
        precio_max = self.request.query_params.get('max_price')
        estado = self.request.query_params.get('estado')
 
        # Filtrar por texto (en título o descripción)
        if texto:
            queryset = queryset.filter(
                Q(title__icontains=texto) |
                Q(description__icontains=texto)
            )
 
        # Filtrar por categoría (por ID o nombre)
        if categoria:
            if categoria.isdigit():
                queryset = queryset.filter(category__id=int(categoria))
            else:
                queryset = queryset.filter(category__name__icontains=categoria)
 
        # Filtrar por rango de precio
        if precio_min:
            queryset = queryset.filter(price__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(price__lte=precio_max)
        
        if estado == "abierta":
            queryset = queryset.filter(closing_date__gt=timezone.now())
        elif estado == "cerrada":
            queryset = queryset.filter(closing_date__lte=timezone.now())
 
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(auctioneer=self.request.user)
    
class UserAuctionListView(APIView): 
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs): 
        # Obtener las subastas del usuario autenticado 
        user_auctions = Auction.objects.filter(auctioneer=request.user) 
        serializer = AuctionListCreateSerializer(user_auctions, many=True) 
        return Response(serializer.data) 

class UserBidListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bids = Bid.objects.filter(bidder=request.user).select_related("auction")
        serializer = UserBidSerializer(bids, many=True)
        return Response(serializer.data)
    

class RatingListCreateView(generics.ListCreateAPIView):
    serializer_class = RatingListCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        auction_id = self.kwargs.get('auction_id')
        return Rating.objects.filter(auction_id=auction_id)

    def perform_create(self, serializer):
        auction_id = self.kwargs.get('auction_id')
        auction = Auction.objects.get(pk=auction_id)
        serializer.save(user=self.request.user, auction=auction)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Calcular la media con Avg
        media = queryset.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 1
        media = round(media, 2)

        return Response({
            "results": serializer.data,
            "media": media
        })


class RatingUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingUpdateRetrieveSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        auction_id = self.kwargs.get('auction_id')
        return Comment.objects.filter(auction_id=auction_id)

    def perform_create(self, serializer):
        auction_id = self.kwargs.get('auction_id')
        serializer.save(user=self.request.user, auction_id=auction_id)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())

class UserCommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        comentarios = Comment.objects.filter(user=request.user).select_related('auction', 'auction__category')
        data = [
            {
                "id": c.id,
                "title": c.title,
                "content": c.content,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "auction": {
                    "id": c.auction.id,
                    "title": c.auction.title,
                    "price": c.auction.price,
                    "category": c.auction.category.name,
                    "is_open": c.auction.closing_date > timezone.now()
                }
            }
            for c in comentarios
        ]
        return Response(data)
    
class UserRatingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ratings = Rating.objects.filter(user=request.user).select_related('auction', 'auction__category')
        data = [
            {
                "id": r.id,
                "rating": r.rating,
                "auction": {
                    "id": r.auction.id,
                    "title": r.auction.title,
                    "price": r.auction.price,
                    "category": r.auction.category.name,
                    "is_open": r.auction.closing_date > timezone.now(),
                }
            }
            for r in ratings
        ]
        return Response(data)

class WalletTransactionView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletTransactionSerializer

    def get_queryset(self):
        return WalletTransaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            transactions = request.user.wallet_transactions.all()
            total = Decimal("0.00")
            for t in transactions:
                if t.amount is not None:
                    total += t.amount if t.is_deposit else -t.amount

            return Response({'saldo_actual': str(round(total, 2))})
        except Exception as e:
            print("💥 Error interno en WalletBalanceView:", str(e))
            return Response({'detail': 'Error interno al calcular el saldo.'}, status=500)


class CobrarSubastaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, auction_id):
        try:
            auction = Auction.objects.get(id=auction_id)
        except Auction.DoesNotExist:
            return Response({"detail": "Subasta no encontrada."}, status=404)

        if auction.closing_date > timezone.now():
            return Response({"detail": "La subasta aún está abierta."}, status=400)

        if request.user != auction.auctioneer and not request.user.is_staff:
            return Response({"detail": "No tienes permiso para cobrar esta subasta."}, status=403)

        highest_bid = auction.bids.order_by("-price").first()
        if not highest_bid:
            return Response({"detail": "La subasta no tiene pujas."}, status=400)

        bidder = highest_bid.bidder
        auctioneer = auction.auctioneer
        amount = highest_bid.price

        # Calcular saldo del pujador
        saldo_pujador = sum([
            t.amount if t.is_deposit else -t.amount
            for t in bidder.wallet_transactions.all()
        ])
        if saldo_pujador < amount:
            return Response({"detail": "El pujador no tiene saldo suficiente para el cobro."}, status=400)

        # Generar transferencia
        WalletTransaction.objects.create(
            user=bidder,
            card_number="COBRO",
            amount=amount,
            is_deposit=False
        )
        WalletTransaction.objects.create(
            user=auctioneer,
            card_number="COBRO",
            amount=amount,
            is_deposit=True
        )

        return Response({"detail": f"Se han transferido {amount}€ al subastador correctamente."}, status=200)

"""
Texto: http://127.0.0.1:8000/api/auctions/?texto=iphone
 
Categorias:
1. Por indice:  http://127.0.0.1:8000/api/auctions/?categoria=2
2. Por nombre: http://127.0.0.1:8000/api/auctions/?categoria=pendientes
 
Precios: http://127.0.0.1:8000/api/auctions/?precioMin=100&precioMax=300
 
Combi: http://127.0.0.1:8000/api/auctions/?texto=pendiente&categoria=pendientes&precioMin=100
"""