from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse

from .models import Transaction, PaymentRequest
from django.contrib import messages
from django.db import transaction as db_transaction
from django.contrib.auth import get_user_model
from decimal import Decimal
from api.views import conversion_view
from django.utils import timezone
from django.test.client import RequestFactory
import json
import urllib.request
import urllib.error

User = get_user_model()

def _convert_amount_internal(from_curr: str, to_curr: str, amount: Decimal) -> Decimal:
    if from_curr == to_curr:
        return amount.quantize(Decimal('0.01'))

    rf = RequestFactory()
    req = rf.get(f'/api/conversion/{from_curr}/{to_curr}/{amount}/')
    resp = conversion_view(req, from_curr, to_curr, str(amount))
    try:
        if getattr(resp, 'status_code', 200) != 200:
            return None
        data = json.loads(resp.content)
        conv = data.get('converted_amount')
        if conv is None:
            return None
        return Decimal(str(conv)).quantize(Decimal('0.01'))
    except Exception:
        return None


def convert_amount(request, amount: Decimal, from_curr: str, to_curr: str) -> Decimal:
    """Convert `amount` from `from_curr` to `to_curr` via the REST service."""
    if from_curr == to_curr:
        return amount.quantize(Decimal('0.01'))

    from_curr = from_curr.upper()
    to_curr = to_curr.upper()
    api_url = request.build_absolute_uri(reverse('api:conversion', args=[from_curr, to_curr, str(amount)]))

    try:
        with urllib.request.urlopen(api_url, timeout=5) as response:
            if response.status != 200:
                return _convert_amount_internal(from_curr, to_curr, amount)
            data = json.loads(response.read().decode())
            conv = data.get('converted_amount')
            if conv is None:
                return _convert_amount_internal(from_curr, to_curr, amount)
            return Decimal(str(conv)).quantize(Decimal('0.01'))
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, json.JSONDecodeError):
        return _convert_amount_internal(from_curr, to_curr, amount)


    

    

    

    

@login_required
def transactions(request):
    """Show transactions involving the current user."""
    qs = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')

    tx_list = []
    user_currency = request.user.currency
    for tx in qs:
        converted = convert_amount(request, tx.amount, tx.currency, user_currency)
        # If conversion unavailable, show original amount
        if converted is None:
            converted = tx.amount.quantize(Decimal('0.01'))
        tx_list.append({'tx': tx, 'converted': converted})

    return render(request, 'transactions.html', {'transactions': tx_list, 'user_currency': user_currency})
    


@login_required
def dashboard(request):
    """Simple account dashboard showing balance, currency, recent transactions and requests."""
    recent = Transaction.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('-created_at')[:5]
    incoming_requests = PaymentRequest.objects.filter(requested_from=request.user, status=PaymentRequest.STATUS_REQUESTED)[:20]
    context = {
        'balance': request.user.balance,
        'currency': request.user.currency,
        'recent_transactions': recent,
        'incoming_requests': incoming_requests,
    }
    return render(request, 'dashboard.html', context)


@login_required
def requests_list(request):
    """List incoming and outgoing pending payment requests for the current user."""
    incoming = PaymentRequest.objects.filter(requested_from=request.user, status=PaymentRequest.STATUS_REQUESTED)
    outgoing = PaymentRequest.objects.filter(requester=request.user, status=PaymentRequest.STATUS_REQUESTED)
    return render(request, 'requests.html', {'incoming_requests': incoming, 'outgoing_requests': outgoing})


@login_required
def cancel_request(request, pk):
    if request.method != 'POST':
        return redirect('payapp:requests')

    pr = get_object_or_404(PaymentRequest, pk=pk)
    if pr.requester != request.user:
        messages.error(request, 'You can only cancel your own requests.')
        return redirect('payapp:requests')

    if pr.status != PaymentRequest.STATUS_REQUESTED:
        messages.error(request, 'Only pending requests can be cancelled.')
        return redirect('payapp:requests')

    pr.delete()
    messages.success(request, 'Request cancelled.')
    return redirect('payapp:requests')


@login_required
def make_payment(request):
    """Placeholder view for making a payment — implement form handling later."""
    if request.method == 'POST':
        to_username = request.POST.get('to_username')
        amount = request.POST.get('amount')
        currency = request.POST.get('currency') or request.user.currency
        try:
            amount_dec = Decimal(amount)
        except Exception:
            messages.error(request, 'Invalid amount')
            return redirect('payapp:make_payment')

        try:
            receiver = User.objects.get(username=to_username)
        except User.DoesNotExist:
            messages.error(request, 'Recipient not found')
            return redirect('payapp:make_payment')

        if request.user == receiver:
            messages.error(request, 'Cannot pay yourself')
            return redirect('payapp:make_payment')

        # determine payer (request.user) and receiver currencies
        payer = request.user
        payer_currency = payer.currency
        receiver_currency = receiver.currency

        # amount_dec is in the payer's currency; ensure sufficient funds
        if payer.balance < amount_dec:
            messages.error(request, 'Insufficient funds')
            return redirect('payapp:make_payment')

        # convert amount to receiver currency for crediting
        credited_amount = convert_amount(request, amount_dec, payer_currency, receiver_currency)
        if credited_amount is None:
            messages.error(request, 'Conversion rate unavailable')
            return redirect('payapp:make_payment')

        # perform transfer atomically: deduct payer (in payer currency), credit receiver (in receiver currency)
        with db_transaction.atomic():
            payer.balance -= amount_dec
            payer.save()

            receiver.balance += credited_amount
            receiver.save()

            tx = Transaction.objects.create(
                sender=payer,
                receiver=receiver,
                amount=amount_dec,
                currency=payer_currency,
                status=Transaction.STATUS_COMPLETED,
            )
        messages.success(request, f'Payment sent to {receiver.username}')
        return redirect('payapp:transactions')

    return render(request, 'make_payment.html')


@login_required
def request_payment(request):
    if request.method == 'POST':
        from_username = request.POST.get('from_username')
        amount = request.POST.get('amount')
        currency = request.POST.get('currency') or request.user.currency
        message = request.POST.get('message', '')
        try:
            amount_dec = Decimal(amount)
        except Exception:
            messages.error(request, 'Invalid amount')
            return redirect('payapp:request_payment')

        try:
            requested_from = User.objects.get(username=from_username)
        except User.DoesNotExist:
            messages.error(request, 'User not found')
            return redirect('payapp:request_payment')

        PaymentRequest.objects.create(
            requester=request.user,
            requested_from=requested_from,
            amount=amount_dec,
            currency=currency,
            message=message,
        )
        messages.success(request, 'Payment request sent')
        return redirect('payapp:dashboard')

    return render(request, 'request_payment.html')

@login_required
def accept_request(request, pk):
    if request.method != 'POST':
        return redirect('payapp:dashboard')

    pr = get_object_or_404(PaymentRequest, pk=pk)
    if pr.requested_from != request.user or pr.status != PaymentRequest.STATUS_REQUESTED:
        messages.error(request, 'Cannot accept this request')
        return redirect('payapp:dashboard')

    requester = pr.requester
    responder = request.user

    # convert requested amount into responder's currency
    amount_to_deduct = convert_amount(request, pr.amount, pr.currency, responder.currency)
    if amount_to_deduct is None:
        messages.error(request, 'Conversion unavailable')
        return redirect('payapp:dashboard')

    if responder.balance < amount_to_deduct:
        messages.error(request, 'Insufficient funds to accept request')
        return redirect('payapp:dashboard')

    with db_transaction.atomic():
        responder.balance -= amount_to_deduct
        responder.save()

        requester.balance += pr.amount
        requester.save()

        Transaction.objects.create(
            sender=responder,
            receiver=requester,
            amount=amount_to_deduct,
            currency=responder.currency,
            status=Transaction.STATUS_COMPLETED,
            reference=f'AcceptedRequest:{pr.id}'
        )
        pr.status = PaymentRequest.STATUS_ACCEPTED
        pr.responded_at = timezone.now()
        pr.save()

    messages.success(request, 'Request accepted and payment made')
    return redirect('payapp:dashboard')


@login_required
def reject_request(request, pk):
    if request.method != 'POST':
        return redirect('payapp:dashboard')
    pr = get_object_or_404(PaymentRequest, pk=pk)
    if pr.requested_from != request.user or pr.status != PaymentRequest.STATUS_REQUESTED:
        messages.error(request, 'Cannot reject this request')
        return redirect('payapp:dashboard')
    pr.status = PaymentRequest.STATUS_REJECTED
    pr.responded_at = timezone.now()
    pr.save()
    messages.info(request, 'Request rejected')
    return redirect('payapp:dashboard')
