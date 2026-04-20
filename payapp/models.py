from django.db import models
from django.conf import settings


# Keep a local currency choice tuple to avoid direct model import cycles
CURRENCY_CHOICES = [
    ('GBP', 'GBP'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
]

class Transaction(models.Model):
    """Represents a completed or pending transfer between users.

    Fields chosen to satisfy brief requirements: sender, receiver, amount, currency, status, timestamp.
    """
    # One payment record is stored for every transfer between users.

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'pending'),
        (STATUS_COMPLETED, 'completed'),
        (STATUS_FAILED, 'failed'),
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender} -> {self.receiver}: {self.amount} {self.currency}'


class PaymentRequest(models.Model):
    """Represents a user requesting payment from another user.

    Includes requester/requestee, amount, currency, message and status so the flow can be accepted/rejected.
    """
    # Payment requests are stored until accepted, rejected, or cancelled.

    STATUS_REQUESTED = 'requested'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_REQUESTED, 'requested'),
        (STATUS_ACCEPTED, 'accepted'),
        (STATUS_REJECTED, 'rejected'),
    ]

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payment_requests_made', on_delete=models.CASCADE)
    requested_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payment_requests_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    message = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'PaymentRequest {self.id} {self.amount} {self.currency}'