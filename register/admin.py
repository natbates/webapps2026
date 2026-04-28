from decimal import Decimal
from django.contrib import admin
from django.contrib.auth import get_user_model

# Note: The coursework requires you to implement admin functionality via views,
# not to rely on Django's admin site. The registration below is provided for
# convenience when developing locally — you may ignore it for marking.

User = get_user_model()


def ensure_default_admin():
    """Ensure a default admin account exists with fixed credentials."""
    # This creates the required admin1/admin1 account after migrations run.
    defaults = {
        'email': 'admin1@example.com',
        'is_staff': True,
        'is_superuser': True,
        'currency': 'GBP',
        'balance': Decimal('500.00'),
    }

    admin, created = User.objects.get_or_create(username='admin1', defaults=defaults)

    if created:
        admin.set_password('admin1')
        admin.save()
        return admin

    updated = False
    if not admin.check_password('admin1'):
        admin.set_password('admin1')
        updated = True

    for field, value in defaults.items():
        if getattr(admin, field) != value:
            setattr(admin, field, value)
            updated = True

    if updated:
        admin.save()

    return admin


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'currency', 'balance')
    search_fields = ('username', 'email')
