from django.db import models
from django.contrib.auth.models import AbstractUser 

class CustomUser(AbstractUser): 
    # models.py
    birth_date = models.DateField(null=True, blank=True)
    locality = models.CharField(max_length=100, blank=True) 
    municipality = models.CharField(max_length=100, blank=True)
