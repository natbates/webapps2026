from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .models import Currency
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction
from payapp.models import Transaction

User = get_user_model()


class RegistrationForm(UserCreationForm):
	currency = forms.ChoiceField(choices=Currency.choices, initial=Currency.GBP)

	class Meta(UserCreationForm.Meta):
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'currency')


def _convert_initial_balance(currency: str) -> Decimal:
	# baseline is 500 GBP; convert to selected currency using simple static rates
	rates = {
		'GBP': Decimal('1.00'),
		'USD': Decimal('1.25'),
		'EUR': Decimal('1.16'),
	}
	rate = rates.get(currency, Decimal('1.00'))
	return (Decimal('500.00') * rate).quantize(Decimal('0.01'))


def register_view(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			with transaction.atomic():
				user = form.save(commit=False)
				# set initial balance according to chosen currency
				selected_currency = form.cleaned_data.get('currency')
				user.currency = selected_currency
				user.balance = _convert_initial_balance(selected_currency)
				user.save()
			login(request, user)
			return redirect('payapp:transactions')
	else:
		form = RegistrationForm()
	return render(request, 'register/register.html', {'form': form})


class CustomLoginView(LoginView):
	template_name = 'register/login.html'

	def form_valid(self, form):
		messages.success(self.request, 'You are now logged in.')
		return super().form_valid(form)


def _is_superuser(u):
	return u.is_active and u.is_superuser


@login_required
@user_passes_test(_is_superuser)
def admin_dashboard(request):
	"""Simple admin dashboard view (lists users and transactions and allows creating admin users)."""
	users = User.objects.all().order_by('username')
	transactions = Transaction.objects.all()[:200]

	message = None
	if request.method == 'POST':
		# Create a new admin user (minimal fields)
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

	return render(request, 'register/admin_dashboard.html', {
		'users': users,
		'transactions': transactions,
		'message': message,
		'currency_choices': Currency.choices,
	})

