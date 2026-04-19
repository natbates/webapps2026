from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from payapp.models import Transaction
from register.models import Currency
from decimal import Decimal

User = get_user_model()


def _convert_initial_balance(currency: str) -> Decimal:
    rates = {
        'GBP': Decimal('1.00'),
        'USD': Decimal('1.25'),
        'EUR': Decimal('1.16'),
    }
    return (Decimal('500.00') * rates.get(currency, Decimal('1.00'))).quantize(Decimal('0.01'))


def _is_superuser(u):
    return u.is_active and u.is_superuser


@login_required
def admin_dashboard(request):
    if not _is_superuser(request.user):
        messages.error(request, 'You must be an administrator to access the admin dashboard.')
        return redirect('payapp:dashboard')

    search_query = request.GET.get('search', '').strip()
    users = User.objects.all().order_by('username')
    if search_query:
        users = users.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query) | Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query))

    users = users.annotate(
        sent_count=Count('sent_transactions', distinct=True),
        received_count=Count('received_transactions', distinct=True),
    )

    transactions = Transaction.objects.all().order_by('-created_at')[:12]
    admin_count = User.objects.filter(is_superuser=True).count()

    message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        currency = request.POST.get('currency') or Currency.GBP
        if username and password:
            new = User.objects.create(username=username, email=email, is_staff=True, is_superuser=True)
            new.set_password(password)
            new.currency = currency
            new.balance = _convert_initial_balance(currency)
            new.save()
            message = f'Created admin {username}'

    return render(request, 'admin_dashboard.html', {
        'users': users,
        'transactions': transactions,
        'admin_count': admin_count,
        'message': message,
        'currency_choices': Currency.choices,
        'search_query': search_query,
    })
