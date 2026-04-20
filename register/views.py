from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from django import forms
from django.db import transaction
from .models import Currency

User = get_user_model()

# Use the custom user model so registration saves balance and currency data.
class RegistrationForm(UserCreationForm):
    currency = forms.ChoiceField(choices=Currency.choices, initial=Currency.GBP)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'currency')

    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput,
        min_length=8,
        help_text='Password must be at least 8 characters.',
    )
    password2 = forms.CharField(
        label='Password confirmation',
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


def _convert_initial_balance(currency: str) -> Decimal:
    rates = {
        'GBP': Decimal('1.00'),
        'USD': Decimal('1.25'),
        'EUR': Decimal('1.16'),
    }
    # Convert the base 500 GBP to the selected registration currency.
    return (Decimal('500.00') * rates.get(currency, Decimal('1.00'))).quantize(Decimal('0.01'))


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                selected_currency = form.cleaned_data.get('currency')
                user.currency = selected_currency
                user.balance = _convert_initial_balance(selected_currency)
                user.save()
            login(request, user)
            return redirect('payapp:dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

