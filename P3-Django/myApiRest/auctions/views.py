from django.shortcuts import render
from rest_framework import generics
from django.utils import timezone
from rest_framework import serializers
from .models import Category, Auction, Bid
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidDetailSerializer, BidListCreateSerializer

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


class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer

class BidListCreate(generics.ListCreateAPIView):
    serializer_class = BidListCreateSerializer

    def get_queryset(self): #sobreescribimos este método para devovler lo que queremos
        return Bid.objects.filter(auction_id=self.kwargs['auction_id']).order_by('-price')
    
    #recibe el serializador #metodo que recibe es POST
    def perform_create(self,serializer): #sobreescribimos este método para crear una puja tenemos que meter el id_auctions
        auction_id=self.kwargs['auction_id'] #tenemos que añadir al POST el id del auction
        serializer.save(auction_id=auction_id)
    

class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidDetailSerializer
    
    def get_queryset(self): #sobreescribimos este método para devovler lo que queremos
        return Bid.objects.filter(auction_id=self.kwargs['auction_id'])
    
    #más validaciones de pujas
    def perform_update(self, serializer):
        bid = self.get_object()
        if bid.auction.close_date < timezone.now():
            raise serializers.ValidationError("No puedes modificar una puja cerrada.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.auction.close_date < timezone.now():
            raise serializers.ValidationError("No puedes borrar una puja cerrada.")
        instance.delete()