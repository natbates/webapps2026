from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser


class Currency(models.TextChoices):
    GBP = 'GBP', 'GBP'
    USD = 'USD', 'USD'
    EUR = 'EUR', 'EUR'


class User(AbstractUser):
    """Custom user extending `AbstractUser`.

    Fields:
    - `balance`: Decimal, default 500.00 (converted by registration logic if needed)
    - `currency`: one of GBP/USD/EUR using `Currency` TextChoices
    """

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('500.00'))
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)

    def __str__(self):
        return self.username
