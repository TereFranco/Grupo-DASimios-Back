from django.shortcuts import render
from rest_framework import generics
from .models import Category, Auction, Bid, Rating
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidDetailSerializer, BidListCreateSerializer, UserBidSerializer, RatingListCreateSerializer, RatingUpdateRetrieveSerializer
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated 
from rest_framework.response import Response 
from .permissions import IsOwnerOrAdmin 
from django.utils import timezone
 
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
        serializer.save(auction=auction, bidder=self.request.user)

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
    

class RatingListCreateView(APIView):
    serializer_class = RatingListCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        auction_id = self.request.query_params.get('auction')
        if auction_id:
            return Rating.objects.filter(auction_id=auction_id)
        return Rating.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RatingUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingUpdateRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self): #sobreescribimos este método para devovler lo que queremos
        return Rating.objects.filter(auction_id=self.kwargs['rating_id'])
   
"""
Texto: http://127.0.0.1:8000/api/auctions/?texto=iphone
 
Categorias:
1. Por indice:  http://127.0.0.1:8000/api/auctions/?categoria=2
2. Por nombre: http://127.0.0.1:8000/api/auctions/?categoria=pendientes
 
Precios: http://127.0.0.1:8000/api/auctions/?precioMin=100&precioMax=300
 
Combi: http://127.0.0.1:8000/api/auctions/?texto=pendiente&categoria=pendientes&precioMin=100
"""