from django.contrib import admin
from .models import Auction, Category, Bid, CustomUser

# Register your models here.
admin.site.register(Auction)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(CustomUser)