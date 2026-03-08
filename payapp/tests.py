from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Transaction, PaymentRequest


class PayappTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        # create two users with different currencies
        self.alice = User.objects.create_user(username='alice', password='pass', currency='GBP')
        self.bob = User.objects.create_user(username='bob', password='pass', currency='USD')
        # set explicit balances
        self.alice.balance = Decimal('500.00')
        self.alice.save()
        self.bob.balance = Decimal('500.00')
        self.bob.save()

    def test_direct_payment_cross_currency(self):
        # alice (GBP) pays bob (USD) 100 GBP -> bob should receive converted amount
        self.client.login(username='alice', password='pass')
        url = reverse('payapp:make_payment')
        resp = self.client.post(url, {'to_username': 'bob', 'amount': '100'})
        self.assertIn(resp.status_code, (302, 301))

        # refresh from db
        from django.contrib.auth import get_user_model
        User = get_user_model()
        alice = User.objects.get(username='alice')
        bob = User.objects.get(username='bob')

        # alice balance reduced by 100
        self.assertEqual(alice.balance.quantize(Decimal('0.01')), Decimal('400.00'))

        # A transaction should exist
        tx = Transaction.objects.filter(sender=alice, receiver=bob).first()
        self.assertIsNotNone(tx)

    def test_request_and_accept(self):
        # alice requests 50 GBP from bob
        self.client.login(username='alice', password='pass')
        url = reverse('payapp:request_payment')
        resp = self.client.post(url, {'from_username': 'bob', 'amount': '50', 'currency': 'GBP', 'message': 'test'})
        self.assertIn(resp.status_code, (302, 301))

        pr = PaymentRequest.objects.filter(requester=self.alice, requested_from=self.bob).first()
        self.assertIsNotNone(pr)
        self.assertEqual(pr.status, PaymentRequest.STATUS_REQUESTED)

        # bob accepts the request
        self.client.logout()
        self.client.login(username='bob', password='pass')
        accept_url = reverse('payapp:accept_request', args=[pr.id])
        resp = self.client.post(accept_url)
        self.assertIn(resp.status_code, (302, 301))

        pr.refresh_from_db()
        self.assertEqual(pr.status, PaymentRequest.STATUS_ACCEPTED)

        # transaction recorded
        tx = Transaction.objects.filter(sender=self.bob, receiver=self.alice).first()
        self.assertIsNotNone(tx)
