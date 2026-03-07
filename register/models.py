from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    CURRENCY_CHOICES = [
        ('GBP', 'British Pounds'),
        ('USD', 'US Dollars'),
        ('EUR', 'Euros'),
    ]
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)  # In GBP initially
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')

    def __str__(self):
        return self.username
