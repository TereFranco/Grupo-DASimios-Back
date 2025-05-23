from django.db import models
from users.models import CustomUser 
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import FileExtensionValidator
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)
    class Meta:
        ordering=('id',)
    def __str__(self):
        return self.name
    

class Auction(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # rating = models.DecimalField(max_digits=3, decimal_places=2)
    stock = models.IntegerField()
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='auctions',
    on_delete=models.CASCADE)
    thumbnail = models.ImageField(
    upload_to='thumbnails/',
    validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
    null=True,
    blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField()
    auctioneer = models.ForeignKey(CustomUser, related_name='auctions', on_delete=models.CASCADE) 

    class Meta:
        ordering=('id',)
    def __str__(self):
        return self.title
    

class Bid(models.Model): 
    auction = models.ForeignKey(Auction, related_name='bids', on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    bidder = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bids")

    class Meta:  
        ordering = ['-price']

    def __str__(self): 
        return f"Bid on {self.auction} by {self.bidder}"


class Rating(models.Model):
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name='ratings', on_delete=models.CASCADE)

    class Meta:  
        unique_together = ('user', 'auction')


class Comment(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auction = models.ForeignKey(Auction, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name="comments", on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.auction}"
    


class WalletTransaction(models.Model):
    user = models.ForeignKey(CustomUser, related_name="wallet_transactions", on_delete=models.CASCADE)
    card_number = models.CharField(max_length=19)  # Se validará que tenga entre 13-19 dígitos
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_deposit = models.BooleanField()  # True = ingreso, False = retiro
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        tipo = "Ingreso" if self.is_deposit else "Retiro"
        return f"{tipo} de {self.amount}€ por {self.user.username}"
