import os
import random
from datetime import timedelta
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapps2026.settings')

import django

django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from register.models import Currency
from payapp.models import Transaction, PaymentRequest

BASE_DIR = Path(__file__).resolve().parent

FIRST_NAMES = [
    'Alice', 'Bob', 'Charlie', 'Dana', 'Evan', 'Fiona', 'George', 'Hannah',
    'Ian', 'Jasmine', 'Kira', 'Leo', 'Maya', 'Noah', 'Olivia', 'Parker',
    'Quinn', 'Riley', 'Sam', 'Tara', 'Uma', 'Vince', 'Will', 'Xena', 'Yara', 'Zane'
]

LAST_NAMES = [
    'Adams', 'Baker', 'Clark', 'Daniels', 'Edwards', 'Foster', 'Garcia', 'Harris',
    'Iverson', 'Johnson', 'King', 'Lewis', 'Miller', 'Nelson', 'Owens', 'Perry',
    'Quincy', 'Reed', 'Smith', 'Turner', 'Underwood', 'Vogel', 'Walker', 'Young', 'Zimmerman'
]

EMAIL_DOMAINS = ['example.com', 'mail.com', 'test.net', 'demo.org']
CURRENCIES = [Currency.GBP, Currency.USD, Currency.EUR]
TRANSACTION_STATUSES = [Transaction.STATUS_COMPLETED, Transaction.STATUS_PENDING, Transaction.STATUS_FAILED]
REQUEST_STATUSES = [PaymentRequest.STATUS_REQUESTED, PaymentRequest.STATUS_ACCEPTED, PaymentRequest.STATUS_REJECTED]


def random_name():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return first, last


def random_email(first, last):
    domain = random.choice(EMAIL_DOMAINS)
    return f'{first.lower()}.{last.lower()}@{domain}'


def random_currency_balance(currency):
    rate = {'GBP': 1.0, 'USD': 1.3, 'EUR': 1.15}.get(currency, 1.0)
    return round(Decimal(str(500.00 * rate)), 2)


def make_users(total=20):
    User = get_user_model()
    users = []
    existing_usernames = set(User.objects.values_list('username', flat=True))
    for _ in range(total):
        first, last = random_name()
        username = f'{first.lower()}{random.randint(100,999)}'
        while username in existing_usernames:
            username = f'{first.lower()}{random.randint(100,999)}'
        email = random_email(first, last)
        currency = random.choice(CURRENCIES)

        user = User.objects.create_user(
            username=username,
            email=email,
            password='password123',
            first_name=first,
            last_name=last,
            currency=currency,
        )
        user.balance = round(random.uniform(200, 1200), 2)
        user.save()
        users.append(user)
        existing_usernames.add(username)

    return users


def make_transactions(users, total=60):
    transactions = []
    for _ in range(total):
        sender, receiver = random.sample(users, 2)
        currency = random.choice(CURRENCIES)
        amount = round(random.uniform(5, 250), 2)
        status = random.choices(
            TRANSACTION_STATUSES,
            weights=[0.7, 0.2, 0.1],
            k=1,
        )[0]

        tx = Transaction(
            sender=sender,
            receiver=receiver,
            amount=amount,
            currency=currency,
            status=status,
            created_at=timezone.now() - timedelta(days=random.randint(0, 45), hours=random.randint(0, 23), minutes=random.randint(0, 59)),
            reference=f'FakeTxn{random.randint(10000,99999)}',
        )
        transactions.append(tx)
    Transaction.objects.bulk_create(transactions)
    return transactions


def make_requests(users, total=40):
    requests = []
    for _ in range(total):
        requester, requested_from = random.sample(users, 2)
        amount = round(random.uniform(5, 250), 2)
        currency = random.choice(CURRENCIES)
        status = random.choices(
            REQUEST_STATUSES,
            weights=[0.6, 0.25, 0.15],
            k=1,
        )[0]
        created_at = timezone.now() - timedelta(days=random.randint(0, 45), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        responded_at = None
        if status != PaymentRequest.STATUS_REQUESTED:
            responded_at = created_at + timedelta(hours=random.randint(1, 72))
            if responded_at > timezone.now():
                responded_at = timezone.now()

        req = PaymentRequest(
            requester=requester,
            requested_from=requested_from,
            amount=amount,
            currency=currency,
            message='Please send the payment when you can.',
            status=status,
            created_at=created_at,
            responded_at=responded_at,
        )
        requests.append(req)
    PaymentRequest.objects.bulk_create(requests)
    return requests


if __name__ == '__main__':
    from decimal import Decimal

    print('Seeding fake data...')
    with transaction.atomic():
        User = get_user_model()
        if not User.objects.filter(username='admin1').exists():
            admin = User.objects.create_superuser('admin1', 'admin1@example.com', 'admin1')
            admin.currency = Currency.GBP
            admin.balance = Decimal('500.00')
            admin.save()
            print('Created default admin1/admin1')

        users = list(get_user_model().objects.filter(is_superuser=False))
        if len(users) < 20:
            created_users = make_users(total=20 - len(users))
            users.extend(created_users)
            print(f'Created {len(created_users)} regular users.')
        else:
            print(f'Found {len(users)} regular users already existing.')

        make_transactions(users, total=60)
        print('Created 60 fake transactions.')

        make_requests(users, total=40)
        print('Created 40 fake payment requests.')

    print('Fake data seeding complete.')
