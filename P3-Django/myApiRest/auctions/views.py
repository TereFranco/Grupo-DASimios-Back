from django.shortcuts import render
from rest_framework import generics
from .models import Category, Auction, Bid
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidDetailSerializer, BidListCreateSerializer
from django.db.models import Q
from rest_framework.exceptions import NotFound
 
# Create your views here.
class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer
 
 
class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
 
 
class AuctionListCreate(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionListCreateSerializer
 
 
# class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Auction.objects.all()
#     serializer_class = AuctionDetailSerializer

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
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
 
    def get_queryset(self): #sobreescribimos este método para devovler lo que queremos
        return Bid.objects.filter(auction_id=self.kwargs['auction_id'])
   
    #recibe el serializador #metodo que recibe es POST
    def perform_create(self,serializer): #sobreescribimos este método para crear una puja tenemos que meter el id_auctions
        auction_id=self.kwargs['auction_id'] #tenemos que añadir al POST el id del auction
        serializer.save(auction_id=auction_id)
   
 
class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidDetailSerializer
   
    def get_queryset(self): #sobreescribimos este método para devovler lo que queremos
        return Bid.objects.filter(auction_id=self.kwargs['auction_id'])
   
 
class AuctionListCreate(generics.ListCreateAPIView):
    serializer_class = AuctionListCreateSerializer
 
    def get_queryset(self):
        queryset = Auction.objects.all()
        texto = self.request.query_params.get('texto')
        categoria = self.request.query_params.get('categoria')
        precio_min = self.request.query_params.get('precioMin')
        precio_max = self.request.query_params.get('precioMax')
 
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
 
 
"""
Texto: http://127.0.0.1:8000/api/auctions/?texto=iphone
 
Categorias:
1. Por indice:  http://127.0.0.1:8000/api/auctions/?categoria=2
2. Por nombre: http://127.0.0.1:8000/api/auctions/?categoria=pendientes
 
Precios: http://127.0.0.1:8000/api/auctions/?precioMin=100&precioMax=300
 
Combi: http://127.0.0.1:8000/api/auctions/?texto=pendiente&categoria=pendientes&precioMin=100
"""